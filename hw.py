import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import time

class HWData():
    def __init__(self, row):
        self._id, self.course, self.name, self.typ, \
                self.due, self.done, self.desc, self.link = row

    def set_data(self, row):
        self.course, self.name, self.typ, \
                self.due, self.done, self.desc, self.link = row

    def get_data(self):     # Get the data inside the instance except the id
        return [self.course, self.name, self.typ, self.due,
                self.done, self.desc, self.link]

    @classmethod
    def new_from_id(cls, cur, ID):
        return cls(cur.execute("""
            SELECT * from hws
                WHERE id = ?""", [ID]).fetchone())

    @staticmethod
    def insert_data(cur, data):
        cur.execute("""
            INSERT INTO hws (course, name, type, due, done, desc, link)
                VALUES (?, ?, ?, ?, ?, ?, ?)""", data)

    def update_data(self, cur):
        cur.execute("""
            UPDATE hws 
            SET course = ?, name = ?, type = ?, due = ?, done = ?, desc = ?, link = ?
                WHERE id = ?""", self.get_data() + [self._id])

    def delete_data(self, cur):
        cur.execute("""
            DELETE FROM hws
                WHERE id = ?""", [self._id])

class HWWindow:
    def __init__(self, app):
        self.builder = builder = app.builder
        self.app = app
        self.cur = app.cur
        self.cur_hw = None  # The current displaying hw instance; for editing
        self.window          = builder.get_object("hw-win")
        self.hw_course_combo = builder.get_object("hw-course-combo")
        self.hw_name         = builder.get_object("hw-name")
        self.hw_type_combo   = builder.get_object("hw-type-combo")
        self.hw_month_combo  = builder.get_object("hw-month-combo")
        self.hw_day_spin     = builder.get_object("hw-day-spin")
        self.hw_hour_spin    = builder.get_object("hw-hour-spin")
        self.hw_desc         = builder.get_object("hw-desc").get_buffer()   # We don't need the textview itself
        self.hw_link_entry   = builder.get_object("hw-link")
        self.hw_link_btn     = builder.get_object("hw-open-link")
        self.hw_ok           = builder.get_object("hw-ok-btn")
        self.hw_delete       = builder.get_object("hw-delete-hw")
        self.hw_done         = builder.get_object("hw-mark-done")
        self.hw_cancel       = builder.get_object("hw-cancel-btn")

        self.hw_ok.      connect("clicked", self.new_hw)
        self.hw_delete.  connect("clicked", self.delete_this)
        self.hw_done.    connect("clicked", self.mark_as_done)
        self.hw_cancel.  connect("clicked", lambda b:self.hide())
        self.hw_link_btn.connect("clicked", self.open_link)
        self.accelgroup = Gtk.AccelGroup()
        self.window.add_accel_group(self.accelgroup)
        self.hw_cancel.add_accelerator("clicked", self.accelgroup, Gdk.keyval_from_name("Escape"), 0, Gtk.AccelFlags.VISIBLE)

    def show_all(self):
        self.window.show_all()

    def hide(self):
        self.window.hide()

    def sqlfetchall(self, *a):          # Another shortcut
        return self.cur.execute(*a).fetchall()

    def show_hw(self, hw=None):
        self.hw_course_combo.get_model().clear()
        courses = [l[0] for l in self.sqlfetchall("SELECT DISTINCT course FROM hws")]
        for course in courses:
            self.hw_course_combo.append_text(course)

        self.cur_hw = hw
        if hw:  # Edit mode
            self.window.set_title("Edit Assignment")
            self.hw_course_combo.set_active(courses.index(hw.course))
            self.hw_name.set_text(hw.name)
            self.hw_type_combo.set_active(hw.typ - 1)
            time_structs = time.localtime(hw.due * 3600)
            self.hw_month_combo.set_active(time_structs[1] - 1)
            self.hw_day_spin.set_value(time_structs[2])
            self.hw_hour_spin.set_value(time_structs[3])
            self.hw_desc.set_text(hw.desc)
            self.hw_link_entry.set_text(hw.link)
            self.hw_done.set_visible(True)
            self.hw_delete.set_visible(True)
        else:
            self.window.set_title("New Assignment")
            cur_time = time.localtime()
            self.hw_month_combo.set_active(cur_time[1] - 1)
            self.hw_day_spin.set_value(cur_time[2])
            self.hw_hour_spin.set_value(cur_time[3] + 1)
            self.hw_done.set_visible(False)
            self.hw_delete.set_visible(False)
        self.show_all()

    def delete_this(self, btn):
        self.cur_hw.delete_data(self.cur)
        self.app.refresh_tree()
        self.hide()

    def mark_as_done(self, btn):
        self.cur_hw.done = True
        self.cur_hw.update_data(self.cur)
        self.app.refresh_tree()
        self.hide()

    def new_hw(self, btn):
        course = self.hw_course_combo.get_active_text()
        name = self.hw_name.get_text()

        if course == "" or name == "":
            print("Course or name can't be empty!")
        typ = self.hw_type_combo.get_active() + 1

        # calculate due
        due_yr, cur_month = time.localtime()[:2]
        due_month = self.hw_month_combo.get_active() + 1    # ID count from 0
        if due_month < cur_month:
            due_yr += 1
        due_index = int(time.mktime((due_yr, due_month,
            self.hw_day_spin.get_value_as_int(),
            self.hw_hour_spin.get_value_as_int(),
            0, 0, 0, 0, 0)) // 3600) - 1    # For a unknown bug in time.mktime()

        desc = self.hw_desc.get_text(*self.hw_desc.get_bounds(), True)
        link = self.hw_link_entry.get_text()

        data_row = [course, name, typ, due_index, False, desc, link]
        if self.cur_hw:     # Currently editing a data
            self.cur_hw.set_data(data_row)
            self.cur_hw.update_data(self.cur)
        else:
            HWData.insert_data(self.cur, data_row)

        self.app.refresh_tree()
        self.hide()

    def open_link(self):
        url = self.hw_link_entry.get_text()
        if url == "":
            return
        m = re.match("^\\w+://", url)
        if m:
            if url[m.endpos():] == "":
                return
        else:
            url = "http://" + url
        web.open(url)

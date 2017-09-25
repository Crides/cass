#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import sys, time, sqlite3 as sql
from hw import *

COLUMN_NAMES = ["Course", "Name", "Type", "Due"]
DB_NAME = ".cass_data.db"

TYPE_TEXTS = ["", "Multiple Choice", "Short Answers", "Essay", "Project"]
TEXT_COLORS = [
        "#000000",  # Black
        "#333333",  # Dark grey
]
TYPE_COLORS = [
        None,       # A place holder; the typs start @ 1
        "#66bb6a",
        "#29b6f6",
        "#ab47bc",
        "#ffee58",
]
BG_COLORS = [
        "#ffffff",  # White
        "#eeeeee",  # Light grey
]
TIME_COLORS = [
        "#4caf50",  # Green
        "#ffeb3b",  # Yellow
        "#f44336",  # Red
        "#b71c1c",  # Dark red
]

def now():  # Return the hour index for now
    return int(time.time() // 3600)

class CASSApp(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self)
        self.builder = Gtk.Builder()
        self.show_tree = True

    def get_object(self, name):     # A short cut
        return self.builder.get_object(name)

    def sqlfetchall(self, *a):      # Another shortcut
        return self.cur.execute(*a).fetchall()

    # Database and TreeModel related methods
    def recreate_table(self):
        # Database structure:
        # ID    | Course  | Name  | Due   | Type    | Description   | Link  | Repeat
        # Courses are inferred from the rows' Course columns
        # Due time is time.time() / 3600 ... we only need precesion to the hours
        # 
        # Tree view structure:
        # Name  | Type  | Due
        # Courses would *only* have Name column, and Type would be 0
        self.cur.executescript("""
            DROP TABLE IF EXISTS hws;
            CREATE TABLE hws (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                course      TEXT NOT NULL DEFAULT "",
                name        TEXT NOT NULL,
                type        TINYINT,
                due         INT,
                done        BOOLEAN,
                desc        TEXT,
                link        TEXT
            );""")

    def refresh_tree(self):
        self.tree_store.clear()
        try:
            if self.show_tree:      # Show courses & hws in tree-style
                iters = {}
                for hw in self.sqlfetchall("""
                    SELECT id, '' AS course, course AS name, 0, 0, done
                        FROM hws
                        GROUP BY course
                        HAVING min(done) == 0 OR max(due) > ?
                    UNION ALL
                    SELECT id, course, name, type, due, done
                        FROM hws
                        WHERE NOT (done AND due < ?)""", [now(), now()]): #  Done and due time passed
                    course, name = hw[1:3]
                    if course == "":
                        iters[name] = self.tree_store.append(None, hw)
                    else:
                        self.tree_store.append(iters[course], hw)
            else:               # Show just hws
                for hw in self.sqlfetchall("""
                    SELECT id, course, name, type, due, done FROM hws
                        WHERE NOT done"""):
                    self.tree_store.append(None, hw)
        except sql.Error as e:
            print(e)
            #self.recreate_table()

    # GUI related methods
    def do_activate(self):
        self.builder.add_from_file("cass.ui")
        self.con = sql.connect(DB_NAME)
        self.cur = self.con.cursor()

        # Bindings
        # Main Window's
        self.get_object("show-tree").connect("toggled", self.switch_tree_view_mode)
        self.get_object("new-hw-btn").connect_object("clicked", self.show_hw, None)
        self.tree_store = self.get_object("hw-store")
        self.tree_view = self.get_object("hw-tree")
        self.tree_view.connect("button-press-event", self.handle_tree_view_click)

        # Homework window
        self.hw_win = HWWindow(self)

        # Show main window
        self.populate_tree_view()
        window = self.get_object("main-window")
        window.set_application(self)
        window.show_all()

    def populate_tree_view(self):
        # Name column
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(COLUMN_NAMES[1], cell, text=2)
        col.set_expand(True)
        col.set_sort_column_id(2)
        col.set_cell_data_func(cell, self.set_name_attr)
        self.tree_view.append_column(col)

        # Type column
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(COLUMN_NAMES[2], cell)
        col.set_property("fixed-width", 120)
        col.set_sort_column_id(3)
        col.set_cell_data_func(cell, self.set_type_attr)
        self.tree_view.append_column(col)

        # Due column
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn(COLUMN_NAMES[3], cell)
        col.set_property("fixed-width", 110)
        col.set_sort_column_id(4)
        col.set_cell_data_func(cell, self.set_due_attr)
        self.tree_view.append_column(col)

        # Read data
        self.refresh_tree()

    def set_name_attr(self, col, cell, model, tree_iter, usrd):
        done = model[tree_iter][5]
        cell.set_property("foreground", TEXT_COLORS[done])  # Grey if done
        cell.set_property("strikethrough", done)            # Strike thru if done
        cell.set_property("background", BG_COLORS[done])    # Grey if done

    def set_type_attr(self, col, cell, model, tree_iter, usrd):
        typ, _, done = model[tree_iter][3:6]
        cell.set_property("text", TYPE_TEXTS[typ])
        cell.set_property("font", "ubuntu mono 10")
        cell.set_property("ypad", 2)
        cell.set_property("xpad", 4)
        cell.set_property("strikethrough", done)            # Strike thru if done
        cell.set_property("background", BG_COLORS[done])    # Grey if done
        if done:
            cell.set_property("foreground", TEXT_COLORS[done])  # Grey if done
        else:
            cell.set_property("foreground", TYPE_COLORS[typ])

    def set_due_attr(self, col, cell, model, tree_iter, usrd):
        due_hour, done = model[tree_iter][4:6]
        time_str = ""
        background = None

        # TODO Optimize this code ...
        if due_hour:
            hour_diff = due_hour - now()
            background = None
            time_structs = time.localtime(due_hour * 3600)
            time_str = time.strftime("%y/%-m/%-d %-I %P", time_structs)
            if done:
                background = BG_COLORS[1]
            else:
                if hour_diff < 0:
                    background = TIME_COLORS[3]      # Overdue
                elif hour_diff < 24:
                    background = TIME_COLORS[2]      # Urgent
                elif hour_diff < 48:
                    background = TIME_COLORS[1]      # Somewhat urgent
                else:
                    background = TIME_COLORS[0]      # Normal
        else:
            background = BG_COLORS[done]
        # TODO ... until here
        cell.set_property("text", time_str)
        cell.set_property("background", background)
        cell.set_property("foreground", TEXT_COLORS[done])
        cell.set_property("strikethrough", done)

    def switch_tree_view_mode(self, btn):
        self.show_tree = btn.get_active()
        if self.show_tree:      # Show Tree
            # Remove the first column i.e. Course
            self.tree_view.remove_column(self.tree_view.get_column(0))
        else:
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(COLUMN_NAMES[0], cell, text=1)
            col.set_sort_column_id(1)
            self.tree_view.insert_column(col, 0)      # Insert the Course column at the front
        self.refresh_tree()

    def handle_tree_view_click(self, view, event):
        if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS: # Left double click
            res = view.get_path_at_pos(event.x, event.y)
            if not res:
                return
            path, col, _, _ = res
            tree_iter = self.tree_store.get_iter(path)
            _hw = self.tree_store[tree_iter][:]     # Slice all of it or it would be a TreeRow
            if _hw[1] == "":    # A course
                if view.row_expanded(path):
                    view.collapse_row(path)
                else:
                    view.expand_row(path, False)
            else:
                hw = HWData.new_from_id(self.cur, _hw[0])
                self.show_hw(hw)

    def show_hw(self, hw):
        self.hw_win.show_hw(hw)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)
        self.con.commit()
        self.con.close()
        self.quit()

sys.exit(CASSApp().run(sys.argv))

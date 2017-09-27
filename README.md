CASS - The Courses' Assignment Scheduling System
------------------------------------------------

# Introduction

This project is created for the purpose of a simple assignment management system, especially for the assignments with different deadline and times and media (i.e. on paper or on a certain website). The project is based on Python and Gtk for GUI and `sqlite` for data storage. It hasn't been ported to other platforms yet, but it should be pretty easy to do so.

# GUI Layout

In the main window, there is a tree-view in the middle displaying all the uncompleted or not due assignments. Three buttons on top of the tree-view are for changing the viewing mode, creating new assignments and viewing past assignments.

In the tree-view, the assignments can either be displayed in a tree-style, with each course as parents and assignments as children, or in a list-style, with each assignment displayed in the view. You can see the assignment type you assigned in the second column and the due date in the third column. If there's only 24 hrs before the due date, the row would be red; if 48 hrs are available, then it would be yellow; if more are available, it would be green. However, if it is overdue and not completed, then it would turn into dark red. If the assignment is completed but it's not due yet, it would be grey and with strikethrough lines--------------------------------------------

# Introduction

This project is created for the purpose of a simple assignment management system, especially for the assignments with different deadline and times and media (i.e. on paper or on a certain website). The project is based on Python and Gtk for GUI and `sqlite` for data storage. It hasn't been ported to other platforms yet, but it should be pretty easy to do so.

# GUI Layout

In the main window, there is a tree-view in the middle displaying all the uncompleted or not due assignments. Three buttons on top of the tree-view are for changing the viewing mode, creating new assignments and viewing past assignments.

In the tree-view, the assignments can either be displayed in a tree-style, with each course as parents and assignments as children, or in a list-style, with each assignment displayed in the view. You can see the assignment type you assigned in the second column and the due date in the third column. If there's only 24 hrs before the due date, the row would be red; if 48 hrs are available, then it would be yellow; if more are available, it would be green. However, if it is overdue and not completed, then it would turn into dark red. If the assignment is completed but it's not due yet, it would be grey and with strikethrough lines.

When creating a new assignment, you can specify the course it is in, the assignment's name, the type, due time. You can also add a description and a associative link. When double clicking on an assignment in the tree-view, you can view the details of the assignment, edit, delete it or mark it as completed.

There is a button on the top right of the window that would show you all the past assignments (completed and due ones) if you click it.

# Contributing

If you like this project, *please* contribute to it! Although it is not large, there can be some bugs. You can open an issue or open a pull request. I also have some poorly written code. If you have any suggestions, please tell me or open a pull request.

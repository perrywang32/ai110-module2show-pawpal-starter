# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial UML design included classes such as Pet, Task, Schedule, and User. The Pet class stored information about each pet. The Task class represented care activities like walks or feeding. The Schedule class managed tasks by date and time. The User class represented the person using PawPal+ and connected them to their pets and tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes. During implementation, I updated the design to better represent how the classes interact and to avoid data consistency issues.
One major change was making each Pet own its list of CareTask objects while also giving each CareTask a reference back to its Pet. This made it easier to determine which pet a task belongs to. I also changed Owner to store a list of Schedule objects instead of a single schedule so the application can manage tasks across multiple days. Finally, I added validation in Schedule.addTask() to ensure a task can only be added to the schedule for its matching date, preventing inconsistent data.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

- My scheduler considers the task date, time, recurrence (once, daily, weekly), and completion status. It also groups tasks from all of the owner's pets into one daily schedule.

- I decided that date and time were the highest priorities because a schedule must show tasks in the correct order. After that, I included recurrence so repeating tasks could automatically generate their next occurrence. Status and conflict detection help organize the schedule but were lower priorities because they do not affect the order of tasks.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
One tradeoff in my scheduler is that `find_conflicts()` only checks for exact time matches. This keeps the algorithm simple and easy to understand, and it returns warning messages instead of crashing the program. Claude suggested a more Pythonic `groupby` version, but that version depends on the tasks already being sorted correctly. I decided the dictionary-based version was better for this project because it is easier to read and less likely to break if the sorting logic changes later. A more advanced version could detect tasks that are close together, such as 9:00 and 9:05, but that would add extra complexity.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
Claude Code's code editing and code review features were the most helpful. It explained the purpose of methods, suggested improvements, and generated implementations for sorting, filtering, recurring tasks, conflict detection, and automated tests. I reviewed each change before accepting it to make sure it matched my design.
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
One suggestion was to rewrite the find_conflicts() method using Python's itertools.groupby. Although it was shorter and slightly more efficient, I decided to keep the dictionary-based implementation because it was easier to understand and did not rely on the tasks already being sorted. This made the code more readable and maintainable for this project.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested the core scheduling behaviors using automated pytest tests. The tests verified that tasks are sorted correctly by time, filtering by pet and completion status works as expected, recurring daily tasks create the next occurrence when completed, and conflict detection identifies tasks scheduled at the same time. These tests were important because they confirmed that the scheduler's main algorithms behaved correctly and continued to work after adding new features.
**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I am very confident that my scheduler works correctly because all 12 automated tests passed successfully. If I had more time, I would add tests for additional edge cases, such as tasks scheduled only a few minutes apart, more complex recurring schedules, and larger numbers of pets and tasks to verify the scheduler still performs correctly.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with how the scheduler evolved from a simple UML design into a working application with sorting, filtering, recurring tasks, conflict detection, and automated tests. The project became more organized as each feature was added and verified.
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I would improve the user interface by allowing users to edit or delete tasks, view schedules for multiple dates more easily, and detect scheduling conflicts that occur within a small time window instead of only exact time matches.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
Working with an AI coding assistant taught me that my role was to act as the lead architect instead of simply accepting generated code. I needed to review suggestions, decide which designs fit the project requirements, test the implementation, and make tradeoffs between simplicity and performance. AI helped speed up development, but I was responsible for making the final design decisions and ensuring the project met all of the assignment requirements.

This reflects the way you actually completed the project: you used Claude to generate and explain code, but you consistently reviewed suggestions, chose between alternatives (such as the find_conflicts() implementation), and kept the design aligned with the assignment.

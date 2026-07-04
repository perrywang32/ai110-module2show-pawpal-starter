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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

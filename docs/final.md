### A synopsis of your project goal(s) [15 pt]
- Our goal was to create a utility for Super Smash Bros Melee to help people of any skill level become more skilled at the game.
### Link to all written status updates [5 pt]
- [status 1](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/status/status1.md)
- [status 2](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/status/status2.md)
- [status 3](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/status/status3.md)
- [status 4](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/status/status4.md)
- [status 5](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/status/status5.md)
- [status 6](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/status/status6.md)
- [Retrospective](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/status/retrospective.md)
### Links to all videos created (see other assignments) [5 pt]
-[Project Showcase Video](https://www.youtube.com/watch?v=8CjRA2EWUTw&feature=youtu.be)
### Project Planning and Execution [15 pt]
- Link to (or markdown version of) [Design Requirements & Specification](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/project.pdf)
- Finalized [Plan of Work](https://github.com/SeniorDesign2023/Slippi_Stats/blob/main/docs/final.pdf)
### Summary of Final Implementation: [40 pt]
- Design: The user interacts with a GUI where they select from a list of characters, attack styles, playstyles (i.e. aggressive, passive, etc), and edgeguard proficiencies, then choose how much frame delay, L cancel rate, tech rate, and perfect block chance that they would like the bot to have, then they start the bot. This interfaces with an external utility called the Slippi emulator, which boots up an image of Super Smash Bros Melee with the generated bot as one of the characters in the queue. When the user starts the match, the bot accesses the CharacterData class to know which of its moves do what, and then the GeneralizedAgent class, with its chosen settings for reference, to know how to apply those moves and battle the user.
- Limitations: Not all parameters allowed in JSON format are utilized (Edgegaurd level, frame delay, attack type always uses 'mixed'). In the case of frame delay this would be trivial to implement but was skipped for higher priority issues. Edgegaurd level is also straightforward, it would involve (semi-subjectively) idenifyting points in our existing logic to break out of to reduce difficulty and skipping based on the JSON input. Attack type can be manually modified in code by editing the RNG table and CharacterData structure to prioritize aeirial vs. ground types, but currently the frontend setting does not apply this. 
- Future Direction: We would love to add an option to have the bot play against itself, this would be a straightfoward addition as we would need to instantiate two agents on different ports and not much else would change. We would also like to improve the bot's skill ceiling, it currently reaches our goal of being better than a level-9 bot but we would like to increase it's range to get closer to 'SmashBot' levels of difficulty that can be tuned down. Our backend framework was designed to allow programming new behaviors ('strategies') easily, our team would like to explore adding additional behavior types, or potentially allowing users to select multiple types and a basic logic for switching between them.
### Statement of Work
- Whole Team
- Our task this semester was to create a user-customizable bot for Super Smash Bros Melee that would be able to play any character and dynamically apply the provided settings during runtime by analyizing the user's actions and reacting accordingly, based on how it was customized to behave.

- 1 per  team member
- Beckham: As team lead I was heavily involved in the planning/design process early on. As we transitioned into development I worked primarily on the backend, programming the GeneralizedAgent and CharacterData classes as well as our default test logic that implement these classes. 
- Michael: I worked loosely with Beckham on the backend, which for me included things like creating and implementing specific logic for individual bots. Also I made the video with the clips that the rest of the group sent me.
- Ben: I am one of the members that has experience with Smash games so I had input especially in the early stages. I helped design and implement the frontend including converting it to a Customtkinter framework.
- Zach: I worked on the framework and frontend of the application, making the initial version of the application to see the feasibility of reading files in Python, and creating most of the interactables on the application to allow the user to customize the bot.
- Kyle: I tried to implement the machine learning aspect into the bots so the bots would be able to play exactly like real human players by learning from the files that Slippi outputs
of the entire game and every button pressed and action performed. I did not have a whole lot of luck with this early on and due to time constraints of trying to get the regular bot
created and ready I moved on from this stretch goal, and aided on the backend side to help create the customizable bot. Beckham wound up making a large push and starting finalizing
the bot and his code differed from mine in a few ways, so most of the work on mine stopped at that point. I also made most of the presentation with some help from the other group
members in ideas and planning and some slides were done by them that I then edited to fit the theme of the rest of the presentation.  
### Reflection on your team's ability to design, implement, and evaluate a solution. [20 pt]
- Front End: We were able to create an easy to use UI that allowed players to create a bot based on their preferences.  It would be easily understandable to any user of Slippi and would look familiar (green).  We made it across the finish line, but we encountered problems with finding time to meet and work together both as a frontend team as well as meeting with the backend folks to make sure that our work would be compatible with their needs. Toward the end we had more success dividing and completing work.
- Back End: We were able to create an efficient and dynamic system that processes JSON files passed by the front end to run a bot that can (almost. minus the previously mentioned limitations) match any configuration of a bot that the user could want. The bot is precise and easy to scale to the correct skill level, and runs very well in 60 fps. We had a vision, and over the course of the semester, we were able to implement that vision and create something useful.
### Lessons Learned
- "If you had to do it all over again"  
	We would be much more consistent about workflow, instead of trying to do so much at the end.  
	Try to find a set time to meet each week. It can be hard to get the whole team together and on the same page.
	Work on actually building simple bots with basic actions during the first semester to get more fimaliar with libmelee.
	Have much better commenting in the code so others can follow along better, this was made more difficult by the naming convention of libmelee, so stronger comments would have
	helped.  
- Advice for future team  
	Treat this class like there is something due every week, not something huge due in 4 months.  
	Try to schedule your meetings with your mentor earlier, as apposed to waiting till 3 days before class.

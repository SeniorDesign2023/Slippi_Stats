### A synopsis of your project goal(s) [15 pt]

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
- Design: 
- Limitations: Not all parameters allowed in JSON format are utilized (Edgegaurd level, frame delay, attack type always uses 'mixed'). In the case of frame delay this would be trivial to implement but was skipped for higher priority issues. Edgegaurd level is also straightforward, it would involve (semi-subjectively) idenifyting points in our existing logic to break out of to reduce difficulty and skipping based on the JSON input. Attack type can be manually modified in code by editing the RNG table and CharacterData structure to prioritize aeirial vs. ground types, but currently the frontend setting does not apply this. 
- Future Direction: We would love to add an option to have the bot play against itself, this would be a straightfoward addition as we would need to instantiate two agents on different ports and not much else would change. We would also like to improve the bot's skill ceiling, it currently reaches our goal of being better than a level-9 bot but we would like to increase it's range to get closer to 'SmashBot' levels of difficulty that can be tuned down. Our backend framework was designed to allow programming new behaviors ('strategies') easily, our team would like to explore adding additional behavior types, or potentially allowing users to select multiple types and a basic logic for switching between them.

### Statement of Work
- Whole Team
- 1 per  team member

### Reflection on your team's ability to design, implement, and evaluate a solution. [20 pt]

### Lessons Learned
- "If you had to do it all over again"
- Advice for future team

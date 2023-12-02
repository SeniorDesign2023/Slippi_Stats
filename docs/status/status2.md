1. Recap of what was planned for the last 3 weeks
   The official Slippi-Launcher team completed their [implementation](https://github.com/project-slippi/slippi-launcher/pull/400) of the SQLite DB
   and plans to make it publicily accessible. With their rapid progress on the features
   we had planned to make part of our project we decided it was redundant to redo their
   work. Looking at other options inspired from our initial stretch goals we investigated
   related papers: [At Human Speed: Deep Reinforcement Learning with Action Delay](https://arxiv.org/pdf/1810.07286.pdf)
   , [Learning to Play Super Smash Bros. Melee with Delayed Actions](https://arxiv.org/pdf/1810.07286.pdf) ,
   [Beating the World’s Best at Super Smash Bros. Melee with Deep Reinforcement Learning](https://arxiv.org/pdf/1702.06230.pdf)
   
3. Tasks completed  
    a) Description of tasks completed (and by whom)  

   Beckham has started interacting with libmelee a library for making AI in
           Slippi, which we plan to use next semester. The library interacts with
           dolphin/Slippi to read gamestate and send controller inputs for designing AI.
           He also read some academic papers relating to Super Smash Brothers AI and ML.
           Beckham and Kyle discussed some of the problems encountered in the papers and
           some novel ways to solve them, Kyle also got a headstart on our planning
           document. Zach created a very simple application window in Python in order
           to test the feasibility of using Python as our front end in order to allow
           for easier integration with libmelee. Michael setup our team meeting.
   
4. Successes  
    a) What were you group accomplishments?

   We had our "come to jesus" moment about the teams trajectory and how we can
           best realign our scope of the project and team dynamics to succeeed in the
           last weeks of the semester and prepare for the next. We were able to reach
           a relative consesnus on which of the 4 paths layed our in our intermediate
           planning document worked as the best fit for everyone.

   The project lead on 'Slippi-Launcher' reached out regarding his teams
           progress on their SQLite DB [implementation](https://github.com/project-slippi/slippi-launcher/pull/400)
           it will be public facing, meaning we can access it from outside applications.
           He also invited our team to work on implementating stat visualization if we
           so wished.
       
   
    b) Were there other things you tried that did not work and why?
           After the Slippi team decided to do our project themselves, one idea
           was to still go ahead and continue doing it anyway. However, we decided
           that probably wasn't the best idea, because of the amount of time to learn
           how to integrate with their existing code and then to create the project
           there would no way for us to produce something of as good quality as they
           would be able to themselves.
   
4) Roadblocks/challenges  
    a) Describe the challenges  

   Having to completely change our idea to something else has been time consuming
           and partially demoralizing. We had high hopes and great communication with the
           Slippi lead about what our project needed, however with their experience and
           resources they were able to complete the bulk of our project ideas in a short
           period of time.
   
    b) Did you overcome them or are there still challenges left?  

   We did mostly overcome it. Having a short meeting and getting all members to
           vote on what the plan should be now and a rough general idea on what part of
           the work each member wants to be tasked with. 
   
    c) Do you need help with it?  Can your mentor help or do you need external help?  

   Our mentor is Ward, and during our last meeting with him he did provide advice
           on how we should proceed from here. This was for his opinion on which of path
           options from here should not be do to time, and encouraged a meeting between
           members to set up a plan and figure out division of labor. As we get more into
           implementation of ML/AI Lars will likely be a great resource.
   
6) Changes/Deviations from the project Pitch

   A rather large deviation from our project pitch occured. Do to the main Slippi
       team deciding to do most of our original pitch themselves, it left us in an
       awkward situation. We have decided to focus on more of the stuff we had planned
       as extra things to try if there was time. Specifically, our focus is now on
       using machine learning and the play files from Slippi matches as a dataset
       to build a model that can be trained to play like a real world player. Whether
       that player is your friend you want to beat, or potentially a pro player (the
       pro player copying will be the most difficult). There has been a few ideas for
       how to accomplish this, and ironing out the specifics is still in the works for
       the final planning document.

   We discussed a novel approach to solving an issue previous academic papers ran
       into when training prediction models off of pro player data. Namely that pro
       players will do certain inputs in sequence MANY times, such as 'wavedashing'
       which involves three extremely rapid inputs of jump->tilt->dodge to be
       effective. Prediction models on this data would then commonly do those three
       actions in sequence throughout combat like a pro player, but to a very negative
       effect as the model did not account for the input needing to be so precise.
       Our novel solution (which we also believe may improve training times to be
       realistic on consumer hardware) is to hardcode multiple AI's for different
       playstyles, such as defensive, recovery, combo, etc. And then instead of
       training a model to output analog and digital button presses, instead output
       which hardcoded AI state to be in, based off which model most matches the
       prior training data in similar states. We plan to elaborate and test the
       validity of this model further in our final planning doc.

9) Confidence on completion of the project for each team member and the group average  
    a) Scale of 1-5; 1 not-confident; 3 = toss-up; 5 = confident.  

   Kyle:    I am still confident we will be able to have a cool project to present
                By April. 5/5  

   Zach:    5/5 I think we have a good diversity of skills amongst our group and I
                believe that we will have a good presentation come April.

   Beckham: 4/5 I am confident in the "manpower" of our group, and that we can
                pull together a solid project by April. To do so though we will need to
                create much better structure for getting everyone to work.

11) Group dynamics  
    a) Is your group working or are there problems?  

    Many of our group members have been extremely busy with othe classes this
        semester, but through our last meeting we have come to an understanding about
        ensuring this Spring semester will require a good amount of real coding time
        to complete the project.

    Effort has been asymetric between group members for this reason, this is likely
        best addressed with better planning and managment of tasks. Setting up a proper
        roadmap and frequent meetings will be key to our success next semester.

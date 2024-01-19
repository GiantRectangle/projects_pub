# Estimate Modeling

there's a good start on the work in floorplan, and you should take a look at the readme there for the specifics, but here I would like to outline some of the important next steps that are on my mind:
1. we need to explore creating a sage estimate programatically so that the model we build will be able to do it. I intend to try python for it. we need a clear outline of the steps, an action plan, and buy-in from the business before attempting this
2. improve the model to include the rest of the logic for floorplate geometry, particularly how to force rooms to borders, and logic for corridors. this will involve building out the classes and methods started in floorplan
3. implement room scaling in the solution. I'm picturing using constraint programming modeling for this
4. add room identifiers to the graphic
5. make the graphic cleaner. perhaps py5 for this?

# Hospital Floorplate Fitter
## STATS
This is a: CS50P Capstone Project

By: Swan Sodja

From: Seattle, WA

Demo URL: https://youtu.be/XUMUG5IIXk8
## THE BASICS: Problem Statement and Scope Definition
As an estimator for a large general contractor, I must at times provide a complete estimate for a project given only minimal information. This process, known as conceptual estimating, is often used to decide whether to proceed with a project at all, to set budgets and secure financing for the work as a whole, and as a basis for design. In practice, conceptual estimating relies heavily on institutional knowledge, in many cases the particular knowledge of one individual within an organization, and is often expressed as the gut-feel or instinct of that individual. The normal challenge is to express what is essentially a guess as information which can be relied upon. I say a better problem to solve is how to actually create reliable information to use in this process. 

No doubt, it's a hard problem, and one with many parts. Therefore, I select a project type for which the rules are very consistant: 
* Hospital Patient Floors. 

And I adjust the scope of my initial effort to:
* Provide a framework within which some of the more generalizable aspects of the problem can be solved:
    * Counts and physical dimensions of room types
    * Total size of floorplate
    * Analysis of quality of fit of all rooms to theoretical floorplate
* STRETCH GOAL:
    * Provide class methods for future efforts

## DESCRIPTION
### Summary
When main() is called, it will do the following:
* Instatiate room objects according to the logic of a hospital patient floor
* Fit rooms to a theoretical floorplate
* Output to terminal analysis of the quality of the fit thereof
* Output to terminal a table showing total size groupped by room type 
* Generate an image of the fit and save to working directory as floorplan.png
### Files
* project.py
* rooms.py
* test_project.py
* requirements.txt
### Libraries
* rectangle_packing_solver <sub>https://libraries.io/pypi/rectangle-packing-solver</sub>
* pandas
* math
* tabulate
### Classes
* The Room class has the following attributes and methods:
    * type: from input, default=None
    * area: from input, required
    * aspect_ratio: from input, required
    * length: calculated in setter
    * width: calculated in setter
    * rotatable: default=True (used in the rectangle_packing_solver to set whether the room may be rotated within the theoretical floorplate)
    * resize(area): method to scale Room object while maintaining aspect_ratio (this is a STRETCH GOAL)
* Each of the other classes is a particular room type, and thus inherits from Room. Each of these has the attributes set according to the logic of a typical hospital floor
### Functions
* generate_counts(beds):
    * requires: beds: integer
    * Contains the logic for the ratios of each suppoting room type to number of patient beds
    * Returns: counts: tuple (beds: integer, num_huc: integer, num_nurse_stn: integer, num_wtg_rm: integer, num_stg_alc: integer, num_brk_rm: integer)
* generate_rooms(beds): 
    * Requires: counts: tuple (beds: integer, num_huc: integer, num_nurse_stn: integer, num_wtg_rm: integer, num_stg_alc: integer, num_brk_rm: integer)
    * Instantiates room objects for each room type
    * Returns:
        * inventory: a list containing all the room objects
        * rooms: a dataframe, index=room_type, columns=total_room_size (this shows the total size of all the rooms for each type)
        * rectangles: a list of tuples with the length, width, and rotatable attributes for all the room objects (this is passed to the rectangle_packing_solver)
        * net_area: total of the area of all the room objects (this is passed to the rectangle_packing_solver)        
* generate_floorplan(rectangles, net_area):
    * Requires:
        * rectangles: a list of tuples (length: float, width: float, rotatable: boolean)
        * net_area: float
    * Generates an image in the cwd called floorplan.png
    * Returns: percent_filled: float

## NEXT STEPS
* Provide logic to solve for addional rules:
    * Short edge of patient rooms must be along border of floorplate
    * Other rooms may not be along border
    * Between center block of rooms and the patient rooms along perimiter, there must be a corridor
* The preceeding requirements seem to want an itterative approach wherein blocks of rooms are solved, and then the resulting blocks are used to solve the overall floor
* All of the above indicates the need for classes to be created for blocks of rooms, and floors themselves
* The resulting rooms need to be scaled to fit the resulting theoretical floorplate. I built a method into the class to be used for this. I'm picturing this as a constraint programming model configured to minimize unused floorplate

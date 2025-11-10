## Reflection:
When I put a two-agent workflow in place, it made it easy to see who did what: the Planner writes a first draft that makes sense and the Reviewer makes sure it's based on facts and can actually be done. The most important thing I learned was how much "teamwork" you can create just by being prompt. Planner's assumptions and budget directly influenced the Reviewer's checks, deltas, and final merge.

I let the Planner reflect my personal trip planning style so the draft felt human and practical. First, I pick a season and check the weather. That guides my packing tips and rainy-day plans. Second, since many Asian cities have lively nightlife, I planned some evenings around night markets, river walks, and late-night districts. Third, I always look for special events, like Japan's summer fireworks festivals, and I plan my day around them with a little extra time before and after. I do specify budget ranges, but I avoid exact minute-level times. Those are brittle and often wrong without live data.

# Challenges:

The Planner sometimes specified hours or prices that were too detailed. I solved this by banning real-time claims in the prompt ("use typical ranges").
Sometimes the reviewer would check too broadly. I took care of that with a Validation Rubric (hours/closures, inter-city travel time, price ranges, passes/reservations) and a List format to make sure the edits were exact and tied to sources.

Creative choices: "Special Event Suggestions" can be used even when the user doesn't know the name. Explicit pacing caps (≤6 major stops/day) and a budget-math spec (daily subtotals → trip total) are also available so the reviewer can catch drift quickly.

# GenAI use:
 I used a GenAI assistant to polish the wording, tighten the headings, and standardize the Markdown layout and prompts. I also ask GenAI about what the standard flow of a Reviewer Agent does and let it give me a summary and an example of how to do it.



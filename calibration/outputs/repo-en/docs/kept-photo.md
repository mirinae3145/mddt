# Which photo is kept

This document is the reference for the rules `pixtwin move` uses to choose the one photo it keeps in each duplicate group.
The other photos of the group go to the [review folder](review-folder.md).

The rules apply in this order:

- **Default**: The photo with the highest resolution is kept.
  - On a resolution tie, the photo with the oldest modification time is kept.
  - On a further tie, the photo with the shortest path is kept.
- **`--prefer PATH`**: Photos under PATH win over the others.
  - The option can be given several times, and an earlier `--prefer` wins over a later one.
  - Among preferred photos, the default rule still decides.
- **`respect_ratings = true`**: A photo with an EXIF rating of 4 or 5 is kept over a higher-resolution photo without such a rating.
  - The option is off by default.

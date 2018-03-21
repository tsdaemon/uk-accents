This repository contains a database of accents for all Ukrainian words and their forms: `data/accents.csv`. The database is extracted from "Digital lexicographic systems Ukrainian language" database https://github.com/LinguisticAndInformationSystems/mphdict. 

To regenerate database, run `chmod +x generate.sh & ./generate.sh`

Database presented in a CSV form with space as a delimiter. Each row contains word and number of character with an accent:

```csv
абаз 2
абаза 2
абазу 2
``` 

Characters are counted starting from zero.

License: http://opensource.org/licenses/MIT

Database `accents.csv` is available under Open Database License http://opendatacommons.org/licenses/odbl/1.0/. All rights on this database content are protected with Database Contents License https://opendatacommons.org/licenses/dbcl/1.0/.
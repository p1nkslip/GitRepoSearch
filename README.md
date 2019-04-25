# GitRepoSearch

### Configure

Update Github Server and API token variable in main.py

```
# Github variables
GIT_SERVER = 'https://api.github.com'
GIT_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### Run

$ `python3 main.py`

```
> help

commands:
======================
quit  rate  searchcode  whoami
```

```
> searchcode <search_term>

# searches for repos related to the search term specified.
# prints a summary of regex/string matches when scan is complete.
```

```
> rate

# displays information about the rate limit status of your Github token.
```

```
> whoami

# displays information about the token in use.

```


Contributing
=============================================================================== 

### Release process

TravisCI pushes tagged commits to [PyPI](https://pypi.org/project/untiler/).

That process will look something like the following:

```sh
git commit -m <commit message>

git tag -a <tag> -m <tag message>
# ie:
git tag -a 1.0.0 -m "Bump version to 1.0.0"

git push --follow-tags
```

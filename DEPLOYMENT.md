# Deployment

Document describing deployment of this repository.

```
$ docker build -t pants1/docker-volume-backup:x.y.z .
$ docker push pants1/docker-volume-backup:x.y.z
```

```
$ git tag -a x.y.z -m "Description"
$ git push origin x.y.z
```
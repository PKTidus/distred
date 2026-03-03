# distred

Project for CSCI 5673

## Goals

### Lightweight Reddit implementation

- Create text posts
- Create subreddits
- Upvote and downvote posts
- Flask with SQLAlchemy

### Architecture

```sh
./
└─── services/
   ├── api-gateway/
   ├── feed-service/
   ├── post-service/
   ├── subreddit-service/
   ├── user-service/
   └── vote-service/
```

| service           | description                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------- |
| api-gateway       | handles incoming requests and routes them to the appropriate service, can horizontally scale |
| feed-service      | generates home feed based does not have its own db                                           |
| post-service      | handles creating and retrieving posts, has its own db                                        |
| subreddit-service | handles creating and retrieving subreddits, has its own db                                   |
| user-service      | handles creating and retrieving users, has its own db                                        |
| vote-service      | handles upvoting and downvoting posts, has its own db                                        |

### Build load balancer on top

- Use NGINX
- Use HAProxy
- Combine
- Original balancer(?)

### Evaluation

- Test performance of various load balancers with 1000 clients creating posts, subreddits and upvoting/downvoting

### Do not do

- Requests per minute per user limit
- Reddit features not mentioned

### Stretch Goals

- Sharding
- Replication
- Cacheing

# MongoDB Schema

Database: `locallens`

## `users`

```text
_id: ObjectId
username: string (unique)
email: string | null
password_hash: bcrypt string
admin: boolean
created_at: datetime
seed_user: boolean (seed users only)
```

## `businesses`

```text
_id: ObjectId
name: string
town: string
address: string
postcode: string
categories: string[]
description: string
location: GeoJSON Point { type: "Point", coordinates: [longitude, latitude] }
price_level: integer 1..4
active: boolean
rating: number 0..5 (denormalised from reviews)
review_count: integer
created_at: datetime
updated_at: datetime
```

## `reviews`

```text
_id: ObjectId
business_id: ObjectId -> businesses._id
user_id: ObjectId -> users._id
rating: integer 1..5
text: string
created_at: datetime
updated_at: datetime
```

## `blacklist`

```text
jti: string (unique)
user_id: ObjectId
expires_at: datetime (TTL index)
created_at: datetime
```

## Indexes

- `users.username` unique.
- `blacklist.jti` unique; `blacklist.expires_at` TTL.
- `businesses.location` 2dsphere.
- text index on business `name`, `description`, `town`.
- compound index on `town` and `categories`.
- compound review index on `business_id` and `created_at`; author index on `user_id`.
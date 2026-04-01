-- Seed initial data for holbertonschool-hbnb
PRAGMA foreign_keys = ON;

-- Insert an administrator user (password hashed with bcrypt)
INSERT OR REPLACE INTO users (id, email, password, first_name, last_name, is_admin, created_at, updated_at) VALUES (
  'user-admin-1',
  'admin@example.com',
  '$2b$12$ZZi.ceAAVlDZD43Uyti7MuIP1Y8hSlNGzhevo9tSzbRK6qK0E/d6i',
  'Admin',
  'User',
  1,
  datetime('now'),
  datetime('now')
);

-- Insert some amenities
INSERT OR REPLACE INTO amenities (id, name, created_at, updated_at) VALUES (
  'amenity-1', 'WiFi', datetime('now'), datetime('now')
);
INSERT OR REPLACE INTO amenities (id, name, created_at, updated_at) VALUES (
  'amenity-2', 'Air conditioning', datetime('now'), datetime('now')
);
INSERT OR REPLACE INTO amenities (id, name, created_at, updated_at) VALUES (
  'amenity-3', 'Swimming Pool', datetime('now'), datetime('now')
);

-- Insert a demo place with a real country value for frontend filtering
INSERT OR REPLACE INTO places (
  id,
  name,
  description,
  country,
  number_rooms,
  number_bathrooms,
  max_guest,
  price_by_night,
  latitude,
  longitude,
  user_id,
  created_at,
  updated_at
) VALUES (
  'place-demo-1',
  'Lisbon Courtyard Studio',
  'Compact studio used for local frontend and SQL testing.',
  'Portugal',
  1,
  1,
  2,
  95,
  38.7223,
  -9.1393,
  'user-admin-1',
  datetime('now'),
  datetime('now')
);

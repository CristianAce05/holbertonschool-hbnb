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

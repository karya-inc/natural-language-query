-- Inserting sample data into the staff table.
INSERT INTO staff (email, role, created_at) VALUES
('alice@company.com', 'Project Manager', '2023-10-01 09:00:00+00'),
('bob@company.com', 'Data Scientist', '2023-10-01 09:15:00+00'),
('carol@company.com', 'Admin', '2023-10-01 09:30:00+00'),
('dave@company.com', 'Project Manager', '2023-10-01 09:45:00+00');

-- Inserting sample data into the workers table.
INSERT INTO workers (email, created_at) VALUES
('worker1@example.com', '2023-10-01 10:00:00+00'),
('worker2@example.com', '2023-10-01 10:05:00+00'),
('worker3@example.com', '2023-10-01 10:10:00+00'),
('worker4@example.com', '2023-10-01 10:15:00+00'),
('worker5@example.com', '2023-10-01 10:20:00+00');

-- Inserting sample data into the projects table.
INSERT INTO projects (name, description, created_at) VALUES
('Sentiment Analysis', 'Classify customer reviews as positive, negative, or neutral.', '2023-10-01 11:00:00+00'),
('Topic Categorization', 'Categorize news articles into topics.', '2023-10-01 11:05:00+00'),
('Spam Detection', 'Identify spam messages.', '2023-10-01 11:10:00+00');

-- Inserting sample data into the project_staff table.
INSERT INTO project_staff (project_id, staff_id) VALUES
(1, 1), -- Alice is assigned to Sentiment Analysis
(1, 3), -- Carol is also assigned to Sentiment Analysis
(2, 2), -- Bob is assigned to Topic Categorization
(2, 3), -- Carol is also assigned to Topic Categorization
(3, 1), -- Alice is assigned to Spam Detection
(3, 4); -- Dave is assigned to Spam Detection

-- Inserting sample data into the datasets table.
INSERT INTO datasets (project_id, name, description, created_at) VALUES
(1, 'E-commerce Reviews', 'Customer reviews from an e-commerce platform.', '2023-10-01 12:00:00+00'),
(1, 'App Feedback', 'User feedback from a mobile app.', '2023-10-01 12:05:00+00'),
(2, 'News Articles', 'Collection of news articles from various sources.', '2023-10-01 12:10:00+00'),
(3, 'Email Messages', 'Emails labeled as spam or not spam.', '2023-10-01 12:15:00+00');

-- Inserting sample data into the labels table.
-- Labels for Sentiment Analysis datasets.
INSERT INTO labels (dataset_id, name, description, created_at) VALUES
(1, 'Positive', 'Positive sentiment.', '2023-10-01 13:00:00+00'),
(1, 'Negative', 'Negative sentiment.', '2023-10-01 13:00:00+00'),
(1, 'Neutral', 'Neutral sentiment.', '2023-10-01 13:00:00+00'),
(2, 'Positive', 'Positive sentiment.', '2023-10-01 13:05:00+00'),
(2, 'Negative', 'Negative sentiment.', '2023-10-01 13:05:00+00'),
(2, 'Neutral', 'Neutral sentiment.', '2023-10-01 13:05:00+00');

-- Labels for Topic Categorization dataset.
INSERT INTO labels (dataset_id, name, description, created_at) VALUES
(3, 'Politics', 'Political news.', '2023-10-01 13:10:00+00'),
(3, 'Sports', 'Sports news.', '2023-10-01 13:10:00+00'),
(3, 'Technology', 'Technology news.', '2023-10-01 13:10:00+00'),
(3, 'Entertainment', 'Entertainment news.', '2023-10-01 13:10:00+00');

-- Labels for Spam Detection dataset.
INSERT INTO labels (dataset_id, name, description, created_at) VALUES
(4, 'Spam', 'Unwanted or unsolicited messages.', '2023-10-01 13:15:00+00'),
(4, 'Not Spam', 'Legitimate messages.', '2023-10-01 13:15:00+00');

-- Inserting sample data into the data_entries table.
-- Data entries for E-commerce Reviews dataset.
INSERT INTO data_entries (dataset_id, text_content, created_at) VALUES
(1, 'Absolutely love this product! High quality and great value.', '2023-10-01 14:00:00+00'),
(1, 'Very disappointed. The item broke after one use.', '2023-10-01 14:05:00+00'),
(1, 'Its okay, does what it says but nothing special.', '2023-10-01 14:10:00+00'),
(1, 'Exceeded my expectations, will buy again.', '2023-10-01 14:15:00+00'),
(1, 'Not worth the money.', '2023-10-01 14:20:00+00');

-- Data entries for App Feedback dataset.
INSERT INTO data_entries (dataset_id, text_content, created_at) VALUES
(2, 'The app crashes frequently on startup.', '2023-10-01 14:25:00+00'),
(2, 'Great user interface and easy to navigate.', '2023-10-01 14:30:00+00'),
(2, 'Needs more features to be useful.', '2023-10-01 14:35:00+00'),
(2, 'Excellent performance after the latest update.', '2023-10-01 14:40:00+00');

-- Data entries for News Articles dataset.
INSERT INTO data_entries (dataset_id, text_content, created_at) VALUES
(3, 'The government passed a new law today.', '2023-10-01 15:00:00+00'),
(3, 'The local team won the championship!', '2023-10-01 15:05:00+00'),
(3, 'A breakthrough in renewable energy technology.', '2023-10-01 15:10:00+00'),
(3, 'The latest blockbuster movie breaks box office records.', '2023-10-01 15:15:00+00');

-- Data entries for Email Messages dataset.
INSERT INTO data_entries (dataset_id, text_content, created_at) VALUES
(4, 'Congratulations! You have won a free cruise. Click here to claim.', '2023-10-01 15:20:00+00'),
(4, 'Reminder: Your appointment is scheduled for tomorrow at 10 AM.', '2023-10-01 15:25:00+00'),
(4, 'Limited-time offer: Get 50% off on all items.', '2023-10-01 15:30:00+00'),
(4, 'Meeting agenda attached for your review.', '2023-10-01 15:35:00+00');

-- Inserting sample data into the annotations table.
-- Annotations for E-commerce Reviews dataset.
INSERT INTO annotations (data_entry_id, label_id, worker_id, created_at) VALUES
(1, 1, 1, '2023-10-01 16:00:00+00'), -- Worker1 labels as Positive
(2, 2, 2, '2023-10-01 16:05:00+00'), -- Worker2 labels as Negative
(3, 3, 3, '2023-10-01 16:10:00+00'), -- Worker3 labels as Neutral
(4, 1, 1, '2023-10-01 16:15:00+00'), -- Worker1 labels as Positive
(5, 2, 2, '2023-10-01 16:20:00+00'); -- Worker2 labels as Negative

-- Annotations for App Feedback dataset.
INSERT INTO annotations (data_entry_id, label_id, worker_id, created_at) VALUES
(6, 2, 4, '2023-10-01 16:25:00+00'), -- Worker4 labels as Negative
(7, 1, 5, '2023-10-01 16:30:00+00'), -- Worker5 labels as Positive
(8, 3, 4, '2023-10-01 16:35:00+00'), -- Worker4 labels as Neutral
(9, 1, 5, '2023-10-01 16:40:00+00'); -- Worker5 labels as Positive

-- Annotations for News Articles dataset.
INSERT INTO annotations (data_entry_id, label_id, worker_id, created_at) VALUES
(10, 4, 1, '2023-10-01 17:00:00+00'), -- Worker1 labels as Politics
(11, 5, 2, '2023-10-01 17:05:00+00'), -- Worker2 labels as Sports
(12, 6, 3, '2023-10-01 17:10:00+00'), -- Worker3 labels as Technology
(13, 7, 4, '2023-10-01 17:15:00+00'); -- Worker4 labels as Entertainment

-- Annotations for Email Messages dataset.
INSERT INTO annotations (data_entry_id, label_id, worker_id, created_at) VALUES
(14, 8, 1, '2023-10-01 17:20:00+00'), -- Worker1 labels as Spam
(15, 9, 2, '2023-10-01 17:25:00+00'), -- Worker2 labels as Not Spam
(16, 8, 3, '2023-10-01 17:30:00+00'), -- Worker3 labels as Spam
(17, 9, 4, '2023-10-01 17:35:00+00'); -- Worker4 labels as Not Spam

-- App crashes during session by worker
INSERT INTO app_crashes (worker_id, timestamp, error_message, stack_trace) VALUES
(1, '2023-10-01 18:00:00+00', 'NullPointerException at line 42', 'java.lang.NullPointerException\n\tat com.example.app.MainActivity.onCreate(MainActivity.java:42)\n\t...'),
(1, '2023-10-01 18:01:00+00', 'NullPointerException at line 42', 'java.lang.NullPointerException\n\tat com.example.app.MainActivity.onCreate(MainActivity.java:42)\n\t...'),
(2, '2023-10-01 18:05:00+00', 'IndexOutOfBoundsException at line 128', 'java.lang.IndexOutOfBoundsException\n\tat com.example.app.ListAdapter.getView(ListAdapter.java:128)\n\t...'),
(3, '2023-10-01 18:10:00+00', 'OutOfMemoryError at line 256', 'java.lang.OutOfMemoryError\n\tat com.example.app.ImageLoader.loadImage(ImageLoader.java:256)\n\t...'),
(4, '2023-10-01 18:15:00+00', 'IllegalArgumentException at line 64', 'java.lang.IllegalArgumentException\n\tat com.example.app.UserManager.addUser(UserManager.java:64)\n\t...'),
(5, '2023-10-01 18:20:00+00', 'NetworkOnMainThreadException at line 89', 'android.os.NetworkOnMainThreadException\n\tat com.example.app.NetworkUtils.fetchData(NetworkUtils.java:89)\n\t...');

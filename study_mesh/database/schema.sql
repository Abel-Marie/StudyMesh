-- User Profile
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    study_goal TEXT,
    hours_per_day REAL,
    days_per_week INTEGER,
    topics TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT CHECK(task_type IN ('daily', 'weekly', 'long-term')) NOT NULL,
    priority INTEGER DEFAULT 0,
    estimated_hours REAL,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'overdue')) DEFAULT 'pending',
    due_date DATE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deadlines (Scholarships, Internships, etc.)
CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    deadline_date DATE NOT NULL,
    category TEXT,
    priority INTEGER DEFAULT 0,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'missed')) DEFAULT 'pending',
    requirements TEXT,
    completed_requirements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Progress History
CREATE TABLE IF NOT EXISTS progress_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    study_hours REAL,
    notes TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- GitHub Activity
CREATE TABLE IF NOT EXISTS github_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,
    commits INTEGER DEFAULT 0,
    repositories TEXT,
    activity_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Research Papers
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT,
    abstract TEXT,
    arxiv_id TEXT UNIQUE,
    pdf_url TEXT,
    published_date DATE,
    summary TEXT,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social Media Posts
CREATE TABLE IF NOT EXISTS social_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT CHECK(platform IN ('linkedin', 'twitter', 'medium')),
    content TEXT NOT NULL,
    achievement TEXT,
    is_posted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reminders
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reminder_type TEXT NOT NULL,
    message TEXT NOT NULL,
    target_date DATE,
    is_active BOOLEAN DEFAULT 1,
    is_dismissed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

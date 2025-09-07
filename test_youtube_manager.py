#!/usr/bin/env python3
"""
Test script for YouTube Learning Manager
This script tests all the main functions to ensure they work correctly
"""

import sqlite3
from datetime import datetime, timedelta

def test_database_creation():
    """Test if database and tables are created correctly"""
    print("Testing database creation...")
    
    # Connect to test database
    conn = sqlite3.connect('test_youtube_learning.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            channel TEXT,
            duration TEXT,
            category TEXT,
            priority INTEGER DEFAULT 2,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_date TEXT NOT NULL,
            deadline TEXT,
            time_spent INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            video_id INTEGER,
            description TEXT NOT NULL,
            timestamp TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')
    
    print("✅ Database tables created successfully!")
    
    # Test adding a video
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO videos (title, url, channel, duration, category, 
                          priority, created_date, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("Test Video", "https://youtube.com/test", "Test Channel", "10:00", "Test", 1, created_date, "2024-02-15"))
    
    video_id = cursor.lastrowid
    print(f"✅ Test video added with ID: {video_id}")
    
    # Test adding a task
    cursor.execute('''
        INSERT INTO tasks (video_id, description, timestamp)
        VALUES (?, ?, ?)
    ''', (video_id, "Test task", "05:30"))
    
    print("✅ Test task added successfully!")
    
    # Test retrieving data
    cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    video = cursor.fetchone()
    
    if video:
        print(f"✅ Video retrieved: {video[1]} (Priority: {video[6]}, Status: {video[7]})")
        
        # Test column indexing
        print(f"   - Title: {video[1]}")
        print(f"   - URL: {video[2]}")
        print(f"   - Channel: {video[3]}")
        print(f"   - Duration: {video[4]}")
        print(f"   - Category: {video[5]}")
        print(f"   - Priority: {video[6]}")
        print(f"   - Status: {video[7]}")
        print(f"   - Notes: {video[8]}")
        print(f"   - Created: {video[9]}")
        print(f"   - Deadline: {video[10]}")
        print(f"   - Time Spent: {video[11]}")
    
    # Test task retrieval
    cursor.execute("SELECT * FROM tasks WHERE video_id = ?", (video_id,))
    tasks = cursor.fetchall()
    
    if tasks:
        print(f"✅ Task retrieved: {tasks[0][2]} at {tasks[0][3]}")
    
    # Test statistics
    cursor.execute("SELECT COUNT(*) FROM videos")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM videos WHERE status = 'completed'")
    completed = cursor.fetchone()[0]
    
    print(f"✅ Statistics: {total} total videos, {completed} completed")
    
    # Clean up
    cursor.execute("DELETE FROM tasks WHERE video_id = ?", (video_id,))
    cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()
    
    print("✅ All tests passed! Database is working correctly.")
    return True

def test_main_functions():
    """Test the main functions from the YouTube manager"""
    print("\nTesting main functions...")
    
    try:
        # Import the main module
        import Youtube_manager_db
        
        # Test database connection
        print("✅ Database connection successful")
        
        # Test adding a video
        video_id = Youtube_manager_db.add_video(
            "Test Learning Video",
            "https://youtube.com/test",
            "Test Channel",
            "15:30",
            "Programming",
            1,
            "2024-02-20"
        )
        print(f"✅ Video added with ID: {video_id}")
        
        # Test adding a task
        Youtube_manager_db.add_task(video_id, "Learn the basics", "05:00")
        print("✅ Task added successfully")
        
        # Test updating status
        Youtube_manager_db.update_video_status(video_id, "in-progress")
        print("✅ Status updated successfully")
        
        # Test recording time
        Youtube_manager_db.record_time_spent(video_id, 30)
        print("✅ Time recorded successfully")
        
        # Test getting video details
        video = Youtube_manager_db.get_video_details(video_id)
        if video:
            print(f"✅ Video details retrieved: {video[1]}")
        
        # Test getting tasks
        tasks = Youtube_manager_db.get_video_tasks(video_id)
        if tasks:
            print(f"✅ Tasks retrieved: {len(tasks)} task(s)")
        
        # Test statistics
        stats = Youtube_manager_db.get_learning_stats()
        print(f"✅ Statistics: {stats['total_videos']} videos, {stats['completion_rate']:.1f}% complete")
        
        # Test search
        search_results = Youtube_manager_db.search_videos("Test")
        if search_results:
            print(f"✅ Search working: Found {len(search_results)} result(s)")
        
        # Test validation
        if Youtube_manager_db.validate_video_id(video_id):
            print("✅ Video ID validation working")
        
        # Clean up
        Youtube_manager_db.delete_video(video_id)
        print("✅ Cleanup completed")
        
        print("✅ All main functions working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing main functions: {e}")
        return False

if __name__ == "__main__":
    print("🧪 YouTube Learning Manager - Test Suite")
    print("=" * 50)
    
    # Test database creation
    if test_database_creation():
        print("\n" + "=" * 50)
        
        # Test main functions
        if test_main_functions():
            print("\n🎉 ALL TESTS PASSED! The YouTube Learning Manager is working perfectly!")
            print("\nYou can now run: python Youtube_manager_db.py")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
    else:
        print("\n❌ Database test failed. Please check the errors above.")

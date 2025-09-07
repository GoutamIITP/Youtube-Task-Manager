import sqlite3
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('youtube_learning.db')
cursor = conn.cursor()

# Enhanced table structure
cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        channel TEXT,
        duration TEXT,
        category TEXT,
        priority INTEGER DEFAULT 2,  -- 1=High, 2=Medium, 3=Low
        status TEXT DEFAULT 'pending',  -- pending, in-progress, completed
        notes TEXT,
        created_date TEXT NOT NULL,
        deadline TEXT,
        time_spent INTEGER DEFAULT 0  -- in minutes
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

# Core Functions
def add_video(title, url, channel=None, duration=None, category=None, 
              priority=2, deadline=None):
    """Add a new learning video to the database"""
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO videos (title, url, channel, duration, category, 
                          priority, created_date, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, url, channel, duration, category, priority, created_date, deadline))
    conn.commit()
    return cursor.lastrowid

def add_task(video_id, description, timestamp=None):
    """Add a task to a specific video"""
    cursor.execute('''
        INSERT INTO tasks (video_id, description, timestamp)
        VALUES (?, ?, ?)
    ''', (video_id, description, timestamp))
    conn.commit()

def update_video_status(video_id, status):
    """Update the status of a video"""
    cursor.execute('''
        UPDATE videos SET status = ? WHERE id = ?
    ''', (status, video_id))
    conn.commit()

def update_task_status(task_id, status):
    """Update the status of a task"""
    cursor.execute('''
        UPDATE tasks SET status = ? WHERE id = ?
    ''', (status, task_id))
    conn.commit()

def record_time_spent(video_id, minutes):
    """Record time spent on a video"""
    cursor.execute('''
        UPDATE videos SET time_spent = time_spent + ? WHERE id = ?
    ''', (minutes, video_id))
    conn.commit()

def delete_video(video_id):
    """Delete a video and all its tasks"""
    cursor.execute("DELETE FROM tasks WHERE video_id = ?", (video_id,))
    cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.commit()

# Advanced Viewing Functions
def list_videos_by_status(status=None):
    """List videos filtered by status"""
    if status:
        cursor.execute("SELECT * FROM videos WHERE status = ? ORDER BY priority, deadline", (status,))
    else:
        cursor.execute("SELECT * FROM videos ORDER BY priority, deadline")
    return cursor.fetchall()

def list_videos_by_category(category):
    """List videos filtered by category"""
    cursor.execute("SELECT * FROM videos WHERE category = ? ORDER BY priority, deadline", (category,))
    return cursor.fetchall()

def get_video_tasks(video_id):
    """Get all tasks for a specific video"""
    cursor.execute("SELECT * FROM tasks WHERE video_id = ?", (video_id,))
    return cursor.fetchall()

def get_upcoming_deadlines(days=7):
    """Get videos with upcoming deadlines"""
    target_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    cursor.execute('''
        SELECT * FROM videos 
        WHERE deadline <= ? AND status != 'completed'
        ORDER BY deadline
    ''', (target_date,))
    return cursor.fetchall()

def search_videos(search_term):
    """Search videos by title or channel"""
    cursor.execute('''
        SELECT * FROM videos 
        WHERE title LIKE ? OR channel LIKE ?
        ORDER BY priority, deadline
    ''', (f'%{search_term}%', f'%{search_term}%'))
    return cursor.fetchall()

# Progress Tracking Functions
def get_learning_stats():
    """Get comprehensive learning statistics"""
    # Total videos
    cursor.execute("SELECT COUNT(*) FROM videos")
    total = cursor.fetchone()[0]
    
    # Completed videos
    cursor.execute("SELECT COUNT(*) FROM videos WHERE status = 'completed'")
    completed = cursor.fetchone()[0]
    
    # Total time spent
    cursor.execute("SELECT SUM(time_spent) FROM videos")
    total_time = cursor.fetchone()[0] or 0
    
    # Pending tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
    pending_tasks = cursor.fetchone()[0]
    
    return {
        'total_videos': total,
        'completed_videos': completed,
        'completion_rate': (completed / total * 100) if total > 0 else 0,
        'total_time_minutes': total_time,
        'pending_tasks': pending_tasks
    }

def get_video_details(video_id):
    """Get detailed information about a specific video"""
    cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    return cursor.fetchone()

def validate_video_id(video_id):
    """Check if a video ID exists in the database"""
    try:
        video_id = int(video_id)
        cursor.execute("SELECT id FROM videos WHERE id = ?", (video_id,))
        return cursor.fetchone() is not None
    except ValueError:
        return False

# Enhanced Main Application
def main():
    print("Welcome to YouTube Learning Manager!")
    print("Your personal learning companion for YouTube videos")
    
    while True:
        print("\n" + "="*50)
        print("YouTube Learning Manager")
        print("="*50)
        print("1. Add New Learning Video")
        print("2. List Videos")
        print("3. Update Video Status")
        print("4. Add Task to Video")
        print("5. View Video Details & Tasks")
        print("6. View Upcoming Deadlines")
        print("7. View Learning Statistics")
        print("8. Search Videos")
        print("9. Record Time Spent")
        print("10. Delete Video")
        print("11. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-11): ")
        
        if choice == '1':
            print("\n--- Add New Learning Video ---")
            title = input("Enter video title: ")
            url = input("Enter video URL: ")
            channel = input("Enter channel name (optional): ")
            duration = input("Enter duration (optional): ")
            category = input("Enter category (optional): ")
            priority = input("Enter priority (1=High, 2=Medium, 3=Low) [2]: ") or "2"
            deadline = input("Enter deadline (YYYY-MM-DD, optional): ")
            notes = input("Enter notes (optional): ")
            
            try:
                video_id = add_video(title, url, channel, duration, category, int(priority), deadline)
                if notes:
                    cursor.execute("UPDATE videos SET notes = ? WHERE id = ?", (notes, video_id))
                    conn.commit()
                print(f"✅ Video added successfully with ID: {video_id}")
                
                # Ask if user wants to add tasks
                while input("\nAdd a task for this video? (y/n): ").lower() == 'y':
                    task_desc = input("Task description: ")
                    timestamp = input("Timestamp (optional, format HH:MM:SS): ")
                    add_task(video_id, task_desc, timestamp)
                    print("✅ Task added!")
            except Exception as e:
                print(f"❌ Error adding video: {e}")
                
        elif choice == '2':
            print("\n--- List Videos ---")
            status_filter = input("Filter by status (pending, in-progress, completed, or leave empty for all): ")
            videos = list_videos_by_status(status_filter if status_filter else None)
            
            if videos:
                print(f"\nFound {len(videos)} video(s):")
                print("-" * 80)
                for video in videos:
                    priority_text = {1: "High", 2: "Medium", 3: "Low"}[video[6]]
                    print(f"ID: {video[0]} | {video[1]} | Status: {video[7]} | Priority: {priority_text} | Deadline: {video[10] or 'None'}")
            else:
                print("No videos found.")
                
        elif choice == '3':
            print("\n--- Update Video Status ---")
            video_id = input("Enter video ID to update: ")
            if not validate_video_id(video_id):
                print("❌ Invalid video ID!")
                continue
            new_status = input("Enter new status (pending, in-progress, completed): ")
            try:
                update_video_status(video_id, new_status)
                print("✅ Status updated successfully!")
            except Exception as e:
                print(f"❌ Error updating status: {e}")
                
        elif choice == '4':
            print("\n--- Add Task to Video ---")
            video_id = input("Enter video ID to add task: ")
            if not validate_video_id(video_id):
                print("❌ Invalid video ID!")
                continue
            task_desc = input("Task description: ")
            timestamp = input("Timestamp (optional, format HH:MM:SS): ")
            try:
                add_task(video_id, task_desc, timestamp)
                print("✅ Task added successfully!")
            except Exception as e:
                print(f"❌ Error adding task: {e}")
                
        elif choice == '5':
            print("\n--- View Video Details & Tasks ---")
            video_id = input("Enter video ID to view details: ")
            if not validate_video_id(video_id):
                print("❌ Invalid video ID!")
                continue
            video = get_video_details(video_id)
            
            if video:
                print(f"\n📹 Video Details:")
                print(f"Title: {video[1]}")
                print(f"URL: {video[2]}")
                print(f"Channel: {video[3] or 'Not specified'}")
                print(f"Duration: {video[4] or 'Not specified'}")
                print(f"Category: {video[5] or 'Not specified'}")
                print(f"Priority: {['High', 'Medium', 'Low'][video[6]-1]}")
                print(f"Status: {video[7]}")
                print(f"Time spent: {video[11]} minutes")
                print(f"Created: {video[9]}")
                print(f"Deadline: {video[10] or 'No deadline'}")
                print(f"Notes: {video[8] or 'No notes'}")
                
                # Show tasks
                tasks = get_video_tasks(video_id)
                if tasks:
                    print(f"\n📋 Tasks ({len(tasks)}):")
                    for task in tasks:
                        print(f"  • {task[2]} [Status: {task[4]}] {f'at {task[3]}' if task[3] else ''}")
                else:
                    print("\n📋 No tasks for this video.")
            else:
                print("❌ Video not found!")
                
        elif choice == '6':
            print("\n--- Upcoming Deadlines ---")
            days = input("Show deadlines within how many days? [7]: ") or "7"
            try:
                videos = get_upcoming_deadlines(int(days))
                if videos:
                    print(f"\nVideos with deadlines in the next {days} days:")
                    print("-" * 60)
                    for video in videos:
                        print(f"ID: {video[0]} | {video[1]} | Deadline: {video[10]}")
                else:
                    print(f"No videos with deadlines in the next {days} days.")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == '7':
            print("\n--- Learning Statistics ---")
            stats = get_learning_stats()
            print(f"📊 Your Learning Progress:")
            print(f"Total videos: {stats['total_videos']}")
            print(f"Completed videos: {stats['completed_videos']}")
            print(f"Completion rate: {stats['completion_rate']:.1f}%")
            print(f"Total time spent: {stats['total_time_minutes']} minutes ({stats['total_time_minutes']/60:.1f} hours)")
            print(f"Pending tasks: {stats['pending_tasks']}")
            
        elif choice == '8':
            print("\n--- Search Videos ---")
            search_term = input("Enter search term (title or channel): ")
            videos = search_videos(search_term)
            if videos:
                print(f"\nFound {len(videos)} video(s) matching '{search_term}':")
                print("-" * 80)
                for video in videos:
                    priority_text = {1: "High", 2: "Medium", 3: "Low"}[video[6]]
                    print(f"ID: {video[0]} | {video[1]} | Channel: {video[3] or 'Unknown'} | Status: {video[7]} | Priority: {priority_text}")
            else:
                print(f"No videos found matching '{search_term}'.")
                
        elif choice == '9':
            print("\n--- Record Time Spent ---")
            video_id = input("Enter video ID: ")
            if not validate_video_id(video_id):
                print("❌ Invalid video ID!")
                continue
            minutes = input("Enter minutes spent: ")
            try:
                record_time_spent(video_id, int(minutes))
                print("✅ Time recorded successfully!")
            except Exception as e:
                print(f"❌ Error recording time: {e}")
                
        elif choice == '10':
            print("\n--- Delete Video ---")
            video_id = input("Enter video ID to delete: ")
            if not validate_video_id(video_id):
                print("❌ Invalid video ID!")
                continue
            confirm = input("Are you sure? This will delete the video and all its tasks! (y/n): ")
            if confirm.lower() == 'y':
                try:
                    delete_video(video_id)
                    print("✅ Video deleted successfully!")
                except Exception as e:
                    print(f"❌ Error deleting video: {e}")
            else:
                print("Deletion cancelled.")
                
        elif choice == '11':
            print("\nThank you for using YouTube Learning Manager!")
            print("Keep learning and growing! 🚀")
            conn.close()
            break
            
        else:
            print("❌ Invalid choice! Please enter a number between 1-11.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        conn.close()
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        conn.close()
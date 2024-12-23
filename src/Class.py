import logging
import hashlib
import pytz
import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
from abc import ABC
from random import randint

class DatabaseConnection:
    """Singleton database connection manager"""
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        """Establish database connection"""
        try:
            self._client = MongoClient("mongodb://localhost:27017/")
            self._db = self._client["todo_list"]
            self._tasks_collection = self._db["tasks"]
            self._users_collection = self._db["users"]
            logging.info("Database connection established successfully.")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise

    @property
    def tasks_collection(self):
        """Getter for tasks collection"""
        return self._tasks_collection

    @property
    def users_collection(self):
        """Getter for users collection"""
        return self._users_collection

class UserManager:
    """Manages user authentication and point tracking"""
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._users_collection = self._db_connection.users_collection
        self._current_user = None

    def _hash_password(self, password):
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        """Register a new user"""
        # Check if username already exists
        existing_user = self._users_collection.find_one({"username": username})
        if existing_user:
            return False, "Username already exists"

        # Create user with initial point structure
        user_data = {
            "username": username,
            "password": self._hash_password(password),
            "point_senin": 0,
            "point_selasa": 0,
            "point_rabu": 0,
            "point_kamis": 0,
            "point_jumat": 0,
            "point_sabtu": 0,
            "point_minggu": 0,
            "last_point_reset": datetime.now(pytz.timezone('Asia/Jakarta'))
        }
        
        self._users_collection.insert_one(user_data)
        return True, "Registration successful"

    def login(self, username, password):
        """Authenticate user"""
        hashed_password = self._hash_password(password)
        user = self._users_collection.find_one({
            "username": username, 
            "password": hashed_password
        })
        
        if user:
            self._current_user = user
            return True, "Login successful"
        return False, "Invalid username or password"

    def _reset_points_if_needed(self):
        """Reset points based on day and time (Sunday at 00:00)"""
        if not self._current_user:
            return

        # Ambil waktu sekarang dalam zona waktu Jakarta
        current_time = datetime.now(pytz.timezone('Asia/Jakarta'))

        # Ambil waktu reset terakhir dari database, jika tidak ada gunakan default hari ini
        last_reset = self._current_user.get('last_point_reset', current_time)

        # Periksa jika waktu sekarang adalah hari Minggu jam 00:00 dan reset belum dilakukan
        is_sunday_midnight = current_time.weekday() == 6 and current_time.hour == 0 and current_time.minute == 0
        reset_not_done_today = current_time.date() != last_reset.date()

        if is_sunday_midnight and reset_not_done_today:
            # Reset semua poin untuk semua hari
            update = {
                "point_senin": 0,
                "point_selasa": 0,
                "point_rabu": 0,
                "point_kamis": 0,
                "point_jumat": 0,
                "point_sabtu": 0,
                "point_minggu": 0,
                "last_point_reset": current_time
            }

            # Update data pengguna di database
            self._users_collection.update_one(
                {"username": self._current_user['username']},
                {"$set": update}
            )

            # Refresh data pengguna aktif
            self._current_user = self._users_collection.find_one(
                {"username": self._current_user['username']}
            )

    def add_daily_points(self, points, username):
        """Add points for the current day"""
        if not username:
            st.warning("Pengguna saat ini belum ditentukan.")
            return False

        # Ensure points are reset if needed
        self._reset_points_if_needed()

        # Determine the current day's point field
        today = datetime.now(pytz.timezone('Asia/Jakarta'))
        day_points_map = {
            0: "point_senin", 
            1: "point_selasa", 
            2: "point_rabu", 
            3: "point_kamis", 
            4: "point_jumat", 
            5: "point_sabtu",
            6: "point_minggu"
        }
        point_field = day_points_map[today.weekday()]
        #st.write(f"Tanggal dan waktu sekarang: {today}")
        #st.write(f"Hari (weekday): {today.weekday()}")

        # Update points
        self._users_collection.update_one(
            {"username": username},
            {"$inc": {point_field: points}}
        )
        return True

    def get_daily_points(self, username):
        user_data = self._users_collection.find_one({"username": username})  # Pastikan username terisi
        if user_data:
            points = {
                "Senin": user_data.get("point_senin", 0),
                "Selasa": user_data.get("point_selasa", 0),
                "Rabu": user_data.get("point_rabu", 0),
                "Kamis": user_data.get("point_kamis", 0),
                "Jumat": user_data.get("point_jumat", 0),
                "Sabtu": user_data.get("point_sabtu", 0),
                "Minggu": user_data.get("point_minggu", 0),
            }
            return points
        return None


class Task(ABC):
    """Abstract base class for tasks"""
    def __init__(self, name, description, priority, deadline, username):
        self._name = name
        self._description = description
        self._priority = priority
        self._deadline = deadline
        self._username = username
        self._point = self._calculate_point()
        self._status = "ongoing"
        self._type = self._determine_type()

    def _calculate_point(self):
        """Calculate points based on priority"""
        priority_points = {
            "rendah": (1, 5),
            "sedang": (6, 10),
            "tinggi": (11, 15)
        }
        min_point, max_point = priority_points.get(self._priority, (1, 5))
        return randint(min_point, max_point)

    def _determine_type(self):
        """Determine task type based on deadline"""
        now = datetime.now()
        if now > self._deadline:
            return "missed"
        elif (self._deadline - now) <= timedelta(hours=24):
            return "urgent"
        return "common"

    @property
    def name(self):
        """Getter for task name"""
        return self._name

    @property
    def point(self):
        """Getter for task points"""
        return self._point

    @property
    def username(self):
        """Getter for username"""
        return self._username

    def get_detailed_info(self):
        """Get detailed task information"""
        return {
            "name": self._name,
            "description": self._description,
            "priority": self._priority,
            "deadline": self._deadline,
            "point": self._point,
            "status": self._status,
            "type": self._type,
            "username": self._username
        }

class ToDoListManager:
    """Manages todo list operations"""
    def __init__(self, username):
        self._db_connection = DatabaseConnection()
        self._tasks_collection = self._db_connection.tasks_collection
        self._username = username
        self._user_manager = UserManager()

    def add_task(self, task):
        """Add a task for the current user"""
        task_data = task.get_detailed_info()
        self._tasks_collection.insert_one(task_data)
        st.text(f"Tugas '{task.name}' berhasil ditambahkan.")

    def mark_task_done(self, task_name):
        """Mark a task as done and update points"""
        task = self._tasks_collection.find_one({
            "name": task_name, 
            "username": self._username
        })
        
        if task and task['type'] != "missed":
            # Add points for completing the task
            self._user_manager.add_daily_points(task['point'],self._username)
            
            # Remove the task
            self._tasks_collection.delete_one({
                "name": task_name, 
                "username": self._username
            })
            st.text(f"Tugas '{task_name}' selesai.")
        else:
            self._tasks_collection.delete_one({
                "name": task_name, 
                "username": self._username
            })
            st.text(f"Tugas Missed '{task_name}' selesai.")
            
    def update_task_types(self):
        """Update task types based on current time"""
        current_time = datetime.now()
        
        # Update tasks to missed if deadline has passed
        self._tasks_collection.update_many(
            {
                "deadline": {"$lt": current_time},
                "type": {"$ne": "missed"}
            },
            {
                "$set": {
                    "type": "missed",
                    "status": "missed",
                    "point": 0
                }
            }
        )
        
        # Update tasks to urgent if within 24 hours
        self._tasks_collection.update_many(
            {
                "deadline": {
                    "$gt": current_time,
                    "$lt": current_time + timedelta(hours=24)
                },
                "type": "common"
            },
            {
                "$set": {
                    "type": "urgent"
                }
            }
        )
            
    def display_tasks(self):
        """Display tasks for the current user with updated types"""
        # Update task types before displaying
        self.update_task_types()
        
        task_types = ["urgent", "common", "missed"]
        total_tasks = 0
        
        for task_type in task_types:
            tasks = self._tasks_collection.find({
                "type": task_type,
                "username": self._username
            })
            
            st.markdown(f"### Tugas {task_type.capitalize()}")
            
            found = False
            for task in tasks:
                found = True
                total_tasks += 1
                
                # Format deadline
                deadline = task['deadline'].astimezone(pytz.timezone('Asia/Jakarta'))
                deadline_str = deadline.strftime("%d %b %Y %H:%M")
                
                # Display task information in a more structured way
                with st.expander(f"**{task['name']}**"):
                    st.markdown(f"""
                    **Nama**     : {task['name']}  
                    **Deskripsi**: {task['description']}  
                    **Deadline** : {deadline_str}  
                    **Status**   : {task['status']}  
                    **Prioritas**: {task['priority']}  
                    **Point**    : {task['point']}
                    """)
                    
                    st.markdown("---")
                if st.button("Selesaikan Tugas"):
                    self.mark_task_done(task['name'])
            
            if not found:
                st.info(f"Tidak ada tugas {task_type}")
                st.markdown("---")
        
        if total_tasks == 0:
            st.success("Tidak ada tugas yang perlu dikerjakan! 🎉")
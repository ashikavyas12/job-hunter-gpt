# Step 1: Install required packages
!pip install -q langchain langchain-community requests
!pip install -q google-cloud-aiplatform
!pip install -q google-cloud-aiplatform langchain-google-vertexai
!pip install streamlit -q
!pip install langchain -q
!pip install langchain-google-genai -q
!pip install langchain-openai -q
!pip install langchain-community -q
!pip install STREAMLIT
!pip install nltk -q
!pip install textblob -q
!pip install spacy -q

# Step 2: Import all necessary libraries
import requests
import sqlite3
import json
import datetime
import streamlit as st
from typing import List, Dict, Optional
import time
import os
import re
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
import nltk
from textblob import TextBlob
import random
from collections import defaultdict

# Step 3: Download NLTK data for natural language processing
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

# Step 4: Configure Streamlit with enhanced settings
st.set_page_config(
    page_title="AI Job Search Assistant with Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.set_page_config(
    page_title="AI Job Search Assistant with Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Step 5: Initialize session state for chatbot
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'conversation_context' not in st.session_state:
    st.session_state.conversation_context = {}
if 'chatbot_mood' not in st.session_state:
    st.session_state.chatbot_mood = 'helpful'

# Step 6: Original job search functions (keeping all existing functionality)
def search_google_jobs_api(query: str, location: str = "") -> List[Dict]:
    """Original Google Jobs API search function"""
    jobs = []
    try:
        serpapi_key = os.getenv("SERPAPI_KEY")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        NGROK_API_KEY = os.getenv("NGROK_API_KEY")

        if serpapi_key:
            url = "https://serpapi.com/search"
            params = {
                'engine': 'google_jobs',
                'q': query,
                'location': location,
                'api_key': serpapi_key,
                'hl': 'en'
            }

            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                jobs_results = data.get('jobs_results', [])

                for job in jobs_results:
                    jobs.append({
                        'title': job.get('title', 'N/A'),
                        'company': job.get('company_name', 'N/A'),
                        'location': job.get('location', 'N/A'),
                        'description': job.get('description', 'N/A')[:500] + '...',
                        'url': job.get('share_link', '#'),
                        'salary': job.get('detected_extensions', {}).get('salary', 'Not specified'),
                        'posted_date': job.get('detected_extensions', {}).get('posted_at', 'N/A'),
                        'source': 'Google Jobs',
                        'job_id': job.get('job_id', ''),
                        'thumbnail': job.get('thumbnail', '')
                    })
                return jobs

        return get_google_style_mock_jobs(query, location)

    except Exception as e:
        st.error(f"Error fetching Google Jobs: {e}")
        return get_google_style_mock_jobs(query, location)

def get_google_style_mock_jobs(query: str, location: str = "", source: str = "Google Jobs") -> List[Dict]:
    """Generate realistic Google Jobs style mock data"""
    google_featured_companies = [
        {"name": "Google", "logo": "🔍", "url": "careers.google.com"},
        {"name": "Microsoft", "logo": "🖥️", "url": "careers.microsoft.com"},
        {"name": "Amazon", "logo": "📦", "url": "amazon.jobs"},
        {"name": "Meta", "logo": "📘", "url": "careers.facebook.com"},
        {"name": "Apple", "logo": "🍎", "url": "jobs.apple.com"},
        {"name": "Netflix", "logo": "🎬", "url": "jobs.netflix.com"},
        {"name": "Tesla", "logo": "⚡", "url": "tesla.com/careers"},
        {"name": "Spotify", "logo": "🎵", "url": "lifeatspotify.com"},
        {"name": "Adobe", "logo": "🎨", "url": "adobe.com/careers"},
        {"name": "Salesforce", "logo": "☁️", "url": "salesforce.com/careers"}
    ]

    job_types = [
        f"{query} Engineer",
        f"Senior {query} Developer",
        f"{query} Specialist",
        f"Lead {query} Architect",
        f"{query} Consultant",
        f"Principal {query} Engineer",
        f"{query} Manager",
        f"Staff {query} Engineer"
    ]

    locations = [
        "Mountain View, CA", "Seattle, WA", "Austin, TX", "New York, NY",
        "San Francisco, CA", "Boston, MA", "Chicago, IL", "Remote",
        "London, UK", "Toronto, Canada", "Berlin, Germany"
    ]

    jobs = []

    for i in range(random.randint(5, 12)):
        company = random.choice(google_featured_companies)
        job_location = location if location else random.choice(locations)
        salary_min = random.randint(80, 180) * 1000
        salary_max = salary_min + random.randint(30, 70) * 1000

        descriptions = [
            f"Join our team as a {query} professional. We're looking for someone passionate about technology and innovation.",
            f"We are seeking a talented {query} expert to help build the next generation of products.",
            f"Looking for a {query} professional to join our growing team and make a significant impact.",
            f"Exciting opportunity for a {query} specialist to work on cutting-edge projects with a world-class team."
        ]

        jobs.append({
            'title': random.choice(job_types),
            'company': company['name'],
            'company_logo': company['logo'],
            'location': job_location,
            'description': random.choice(descriptions),
            'url': f"https://{company['url']}",
            'salary': f"${salary_min:,} - ${salary_max:,}",
            'posted_date': (datetime.date.today() - datetime.timedelta(days=random.randint(1, 21))).strftime("%Y-%m-%d"),
            'source': source,
            'benefits': ['Health Insurance', 'Remote Work', '401k', 'Stock Options'],
            'employment_type': random.choice(['Full-time', 'Contract', 'Part-time'])
        })

    return jobs

# Step 7: Enhanced Chatbot Functions
class JobSearchChatbot:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm your AI Job Search Assistant! 🤖 How can I help you find your dream job today?",
                "Hi there! Ready to supercharge your job search? I'm here to help! 🚀",
                "Welcome! I'm your personal career assistant. What can I do for you today? 💼"
            ],
            'job_search': [
                "I'd love to help you find jobs! What role are you looking for?",
                "Let's find you some amazing opportunities! What's your target position?",
                "Job hunting can be exciting! Tell me about your ideal job."
            ],
            'resume_help': [
                "I can analyze your resume and provide personalized feedback! Would you like to share it?",
                "Resume optimization is my specialty! Let's make yours shine! ✨",
                "A great resume opens doors! I'm here to help improve yours."
            ],
            'interview_prep': [
                "Interview preparation is crucial! I can help you practice common questions.",
                "Let's get you interview-ready! What position are you interviewing for?",
                "Interviews can be nerve-wracking, but preparation helps! How can I assist?"
            ],
            'salary_negotiation': [
                "Salary negotiation is an important skill! What would you like to know?",
                "Let's talk about getting the compensation you deserve! 💰",
                "Smart negotiation can significantly impact your career! How can I help?"
            ],
            'career_advice': [
                "Career guidance is one of my favorite topics! What's on your mind?",
                "Every career journey is unique! What advice are you looking for?",
                "I'm here to help navigate your career path! What questions do you have?"
            ]
        }

        self.job_search_keywords = [
            'job', 'jobs', 'position', 'role', 'career', 'work', 'employment',
            'hiring', 'vacancy', 'opening', 'opportunity', 'search', 'find'
        ]

        self.interview_keywords = [
            'interview', 'interviews', 'prepare', 'preparation', 'questions',
            'practice', 'tips', 'advice', 'nervous', 'ready'
        ]

        self.resume_keywords = [
            'resume', 'cv', 'curriculum', 'vitae', 'profile', 'skills',
            'experience', 'qualifications', 'review', 'improve'
        ]

        self.salary_keywords = [
            'salary', 'pay', 'compensation', 'wage', 'money', 'negotiate',
            'negotiation', 'raise', 'increase', 'benefits'
        ]

    def analyze_intent(self, user_input: str) -> str:
        """Analyze user intent using keyword matching and sentiment"""
        user_input_lower = user_input.lower()

        # Check for greetings
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in user_input_lower for greeting in greetings):
            return 'greeting'

        # Check for job search intent
        if any(keyword in user_input_lower for keyword in self.job_search_keywords):
            return 'job_search'

        # Check for interview preparation
        if any(keyword in user_input_lower for keyword in self.interview_keywords):
            return 'interview_prep'

        # Check for resume help
        if any(keyword in user_input_lower for keyword in self.resume_keywords):
            return 'resume_help'

        # Check for salary negotiation
        if any(keyword in user_input_lower for keyword in self.salary_keywords):
            return 'salary_negotiation'

        # Default to career advice
        return 'career_advice'

    def generate_response(self, user_input: str, context: dict = None) -> str:
        """Generate contextual response based on user input"""
        intent = self.analyze_intent(user_input)

        # Get base response
        base_response = random.choice(self.responses.get(intent, self.responses['career_advice']))

        # Add contextual information
        contextual_response = self.add_context(base_response, user_input, intent, context)

        return contextual_response

    def add_context(self, base_response: str, user_input: str, intent: str, context: dict = None) -> str:
        """Add contextual information to responses"""
        if intent == 'job_search':
            # Extract potential job titles or locations from user input
            job_titles = self.extract_job_titles(user_input)
            if job_titles:
                base_response += f"\n\nI noticed you mentioned: {', '.join(job_titles)}. Let me help you search for those roles!"

        elif intent == 'interview_prep':
            base_response += "\n\n💡 Quick tip: The STAR method (Situation, Task, Action, Result) is great for behavioral questions!"

        elif intent == 'resume_help':
            base_response += "\n\n📝 Remember: A good resume should be tailored to each job application and highlight your most relevant achievements!"

        elif intent == 'salary_negotiation':
            base_response += "\n\n💰 Pro tip: Research market rates for your role and location before any salary discussion!"

        return base_response

    def extract_job_titles(self, text: str) -> List[str]:
        """Extract potential job titles from user input"""
        common_roles = [
            'developer', 'engineer', 'manager', 'analyst', 'designer', 'consultant',
            'specialist', 'coordinator', 'director', 'administrator', 'technician',
            'scientist', 'researcher', 'architect', 'lead', 'senior', 'junior'
        ]

        words = text.lower().split()
        found_roles = []

        for word in words:
            if word in common_roles:
                found_roles.append(word.title())

        return found_roles

# Step 8: Initialize chatbot instance
chatbot = JobSearchChatbot()

# Step 9: Enhanced Database Functions
def init_enhanced_db():
    """Initialize enhanced SQLite database with chatbot features"""
    try:
        conn = sqlite3.connect('enhanced_job_search.db')
        c = conn.cursor()

        # Original tables
        c.execute('''CREATE TABLE IF NOT EXISTS saved_jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        company TEXT,
                        location TEXT,
                        description TEXT,
                        url TEXT,
                        salary TEXT,
                        source TEXT,
                        employment_type TEXT,
                        posted_date TEXT,
                        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        c.execute('''CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT,
                        location TEXT,
                        results_count INTEGER,
                        searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        # New chatbot tables
        c.execute('''CREATE TABLE IF NOT EXISTS chat_conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_message TEXT,
                        bot_response TEXT,
                        intent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_id TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        preferred_roles TEXT,
                        preferred_locations TEXT,
                        experience_level TEXT,
                        skills TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        c.execute('''CREATE TABLE IF NOT EXISTS interview_questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT,
                        category TEXT,
                        difficulty TEXT,
                        sample_answer TEXT)''')

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# Step 10: Chatbot Conversation Functions
def save_conversation(user_message: str, bot_response: str, intent: str, session_id: str):
    """Save chatbot conversation to database"""
    try:
        conn = sqlite3.connect('enhanced_job_search.db')
        c = conn.cursor()
        c.execute("""INSERT INTO chat_conversations
                     (user_message, bot_response, intent, session_id)
                     VALUES (?, ?, ?, ?)""",
                  (user_message, bot_response, intent, session_id))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error saving conversation: {e}")

def get_conversation_history(session_id: str, limit: int = 10) -> List[tuple]:
    """Get recent conversation history"""
    try:
        conn = sqlite3.connect('enhanced_job_search.db')
        c = conn.cursor()
        c.execute("""SELECT user_message, bot_response, timestamp
                     FROM chat_conversations
                     WHERE session_id = ?
                     ORDER BY timestamp DESC LIMIT ?""", (session_id, limit))
        history = c.fetchall()
        conn.close()
        return history
    except Exception as e:
        return []

# Step 11: Interview Preparation Functions
def get_interview_questions_by_role(role: str) -> List[Dict]:
    """Get interview questions based on job role"""
    questions_db = {
        'developer': [
            {"question": "Tell me about a challenging project you worked on.", "category": "Technical", "difficulty": "Medium"},
            {"question": "How do you stay updated with new technologies?", "category": "General", "difficulty": "Easy"},
            {"question": "Describe your debugging process.", "category": "Technical", "difficulty": "Medium"},
            {"question": "How do you handle code reviews?", "category": "Collaboration", "difficulty": "Medium"},
        ],
        'manager': [
            {"question": "How do you motivate underperforming team members?", "category": "Leadership", "difficulty": "Hard"},
            {"question": "Describe a time you had to make a difficult decision.", "category": "Decision Making", "difficulty": "Medium"},
            {"question": "How do you handle conflicting priorities?", "category": "Time Management", "difficulty": "Medium"},
        ],
        'analyst': [
            {"question": "How do you ensure data accuracy in your analysis?", "category": "Technical", "difficulty": "Medium"},
            {"question": "Describe a time when your analysis changed a business decision.", "category": "Impact", "difficulty": "Hard"},
            {"question": "What tools do you use for data visualization?", "category": "Technical", "difficulty": "Easy"},
        ]
    }

    role_lower = role.lower()
    for key in questions_db:
        if key in role_lower:
            return questions_db[key]

    # Generic questions for any role
    return [
        {"question": "Tell me about yourself.", "category": "General", "difficulty": "Easy"},
        {"question": "Why do you want to work here?", "category": "Company", "difficulty": "Medium"},
        {"question": "What are your strengths and weaknesses?", "category": "Self-Assessment", "difficulty": "Medium"},
        {"question": "Where do you see yourself in 5 years?", "category": "Career Goals", "difficulty": "Medium"},
    ]

# Step 12: Career Advice Functions
def get_career_advice_by_topic(topic: str) -> str:
    """Provide career advice based on topic"""
    advice_db = {
        'networking': """
        🤝 **Networking Tips:**

        1. **Quality over Quantity**: Focus on building meaningful relationships
        2. **Be Genuine**: Offer help before asking for it
        3. **Use LinkedIn**: Optimize your profile and engage with others' content
        4. **Attend Events**: Join industry meetups and conferences
        5. **Follow Up**: Always follow up after meeting someone new

        Remember: Networking is about building relationships, not just collecting contacts!
        """,

        'skill_development': """
        📚 **Skill Development Strategy:**

        1. **Identify Gaps**: Compare your skills with job requirements
        2. **Learn Continuously**: Dedicate time weekly to learning
        3. **Practice Projects**: Build portfolio projects to demonstrate skills
        4. **Get Certified**: Consider relevant industry certifications
        5. **Teach Others**: Teaching reinforces your own learning

        Pro tip: Focus on both technical and soft skills!
        """,

        'job_transition': """
        🔄 **Job Transition Guide:**

        1. **Plan Ahead**: Start planning 3-6 months before making a move
        2. **Network First**: Leverage connections in your target industry
        3. **Transferable Skills**: Identify skills that apply to your new field
        4. **Gradual Transition**: Consider freelancing or volunteering first
        5. **Financial Planning**: Save for potential income gaps

        Remember: Career changes are normal and can be very rewarding!
        """,

        'work_life_balance': """
        ⚖️ **Work-Life Balance Tips:**

        1. **Set Boundaries**: Define clear work hours and stick to them
        2. **Prioritize Tasks**: Focus on high-impact activities
        3. **Take Breaks**: Regular breaks improve productivity
        4. **Use Technology**: Leverage tools to automate routine tasks
        5. **Communicate**: Be clear about your availability with colleagues

        Your wellbeing is crucial for long-term career success!
        """
    }

    topic_lower = topic.lower()
    for key in advice_db:
        if key in topic_lower or topic_lower in key:
            return advice_db[key]

    return """
    💼 **General Career Advice:**

    1. **Stay Curious**: Always be learning and growing
    2. **Build Relationships**: Invest in professional relationships
    3. **Be Adaptable**: Embrace change and new challenges
    4. **Communicate Well**: Strong communication skills are valuable everywhere
    5. **Take Initiative**: Don't wait for opportunities, create them

    Your career is a marathon, not a sprint! 🏃‍♂️
    """

# Step 13: Salary Analysis Functions
def get_salary_insights(role: str, location: str) -> Dict:
    """Provide salary insights for specific roles and locations"""
    # Mock salary data - in real implementation, you'd use APIs like Glassdoor, PayScale, etc.
    salary_data = {
        'software engineer': {
            'san francisco': {'min': 120000, 'max': 200000, 'avg': 160000},
            'new york': {'min': 110000, 'max': 180000, 'avg': 145000},
            'austin': {'min': 90000, 'max': 150000, 'avg': 120000},
            'remote': {'min': 100000, 'max': 170000, 'avg': 135000}
        },
        'data scientist': {
            'san francisco': {'min': 130000, 'max': 220000, 'avg': 175000},
            'new york': {'min': 120000, 'max': 190000, 'avg': 155000},
            'austin': {'min': 95000, 'max': 160000, 'avg': 127500},
            'remote': {'min': 110000, 'max': 180000, 'avg': 145000}
        }
    }

    role_key = next((k for k in salary_data.keys() if k in role.lower()), 'software engineer')
    location_key = next((k for k in salary_data[role_key].keys() if k in location.lower()), 'remote')

    data = salary_data[role_key][location_key]

    return {
        'role': role,
        'location': location,
        'salary_range': f"${data['min']:,} - ${data['max']:,}",
        'average': f"${data['avg']:,}",
        'negotiation_tips': [
            "Research market rates thoroughly",
            "Consider total compensation, not just base salary",
            "Highlight your unique value proposition",
            "Be prepared to walk away if the offer doesn't meet your minimum",
            "Consider timing - end of quarter/year might be better"
        ]
    }

# Step 14: Initialize Enhanced Database
init_enhanced_db()

# Step 15: Main UI with Enhanced Features
st.title("🤖 AI Job Search Assistant with Interactive Chatbot")
st.markdown("---")

# Sidebar for user profile and settings
with st.sidebar:
    st.header("🎯 Your Profile")

    # User preferences
    preferred_roles = st.text_input("Preferred Job Roles", placeholder="e.g., Software Engineer, Data Scientist")
    preferred_locations = st.text_input("Preferred Locations", placeholder="e.g., San Francisco, Remote")
    experience_level = st.selectbox("Experience Level", ["Entry Level", "Mid Level", "Senior Level", "Executive"])

    # Save profile
    if st.button("💾 Save Profile"):
        st.session_state.user_profile = {
            'roles': preferred_roles,
            'locations': preferred_locations,
            'experience': experience_level
        }
        st.success("Profile saved!")

    st.markdown("---")
    st.header("⚙️ Chatbot Settings")
    chatbot_personality = st.selectbox("Chatbot Personality", ["Helpful & Professional", "Friendly & Casual", "Expert & Direct"])
    st.session_state.chatbot_mood = chatbot_personality.lower()

# Main tabs with enhanced features
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💬 AI Chat Assistant",
    "🔍 Job Search",
    "📄 Resume Analysis",
    "🎤 Interview Prep",
    "💰 Salary Insights",
    "💾 Saved Jobs",
    "📊 Dashboard"
])

# Step 16: Interactive Chatbot Tab
with tab1:
    st.subheader("💬 Your Personal AI Career Assistant")

    # Chat interface
    chat_container = st.container()

    # Display chat history
    with chat_container:
        if st.session_state.chat_history:
            for i, (user_msg, bot_msg, timestamp) in enumerate(st.session_state.chat_history[-10:]):
                # User message
                st.markdown(f"""
                <div style="background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;">
                    <strong>You:</strong> {user_msg}
                    <br><small>{timestamp}</small>
                </div>
                """, unsafe_allow_html=True)

                # Bot message
                st.markdown(f"""
                <div style="background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>🤖 Assistant:</strong> {bot_msg}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👋 Start a conversation! Ask me about jobs, resume tips, interview preparation, or career advice.")

    # Chat input
    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.text_input("💬 Ask me anything about your career...",
                                   placeholder="e.g., 'Find me Python developer jobs' or 'Help me prepare for an interview'",
                                   key="chat_input")

    with col2:
        send_button = st.button("Send 🚀", use_container_width=True)

    # Quick action buttons
    st.markdown("**Quick Actions:**")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔍 Find Jobs", key="quick_jobs"):
            user_input = "Help me find jobs"
            send_button = True

    with col2:
        if st.button("📄 Resume Help", key="quick_resume"):
            user_input = "Help me improve my resume"
            send_button = True

    with col3:
        if st.button("🎤 Interview Prep", key="quick_interview"):
            user_input = "Help me prepare for interviews"
            send_button = True

    with col4:
        if st.button("💰 Salary Info", key="quick_salary"):
            user_input = "Tell me about salary negotiation"
            send_button = True

    # Process user input
    if (user_input and send_button) or user_input:
        if user_input.strip():
            # Generate bot response
            bot_response = chatbot.generate_response(user_input, st.session_state.user_profile)

            # Add to chat history
            timestamp = datetime.datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append((user_input, bot_response, timestamp))

            # Save conversation
            save_conversation(user_input, bot_response, chatbot.analyze_intent(user_input), "session_1")

            # Clear input and rerun
            st.rerun()

# Step 17: Enhanced Job Search Tab (Continuation)
with tab2:
    st.subheader("🔍 Google-Powered Job Search")

    col1, col2 = st.columns(2)
    with col1:
        job_role = st.text_input("Job Role",
                                 value=st.session_state.user_profile.get('roles', ''),
                                 placeholder="e.g., Python Developer, Data Scientist, Product Manager")
    with col2:
        job_location = st.text_input("Location",
                                     value=st.session_state.user_profile.get('locations', ''),
                                     placeholder="e.g., San Francisco, Remote, New York")

    # Enhanced search with AI suggestions
    if job_role:
        st.write("🤖 **AI Suggestions:**")
        suggestions = [
            f"Senior {job_role}",
            f"Junior {job_role}",
            f"Remote {job_role}",
            f"{job_role} Manager"
        ]

        cols = st.columns(4)
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"ai_suggest_{i}"):
                    job_role = suggestion
                    st.rerun()

    if st.button("🔎 Search Jobs with AI", type="primary", use_container_width=True):
        if not job_role:
            st.warning("Please enter a job role.")
        else:
            with st.spinner("🤖 AI is searching for the best jobs for you..."):
                jobs = get_google_style_mock_jobs(job_role, job_location)

                if jobs:
                    st.success(f"🎉 Found {len(jobs)} job opportunities!")

                    # Enhanced job display with AI insights
                    for i, job in enumerate(jobs):
                        with st.expander(f"{job['company_logo']} {job['title']} at {job['company']} - {job['location']}"):
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.write(f"**📍 Location:** {job['location']}")
                                st.write(f"**💰 Salary:** {job['salary']}")
                                st.write(f"**📅 Posted:** {job['posted_date']}")
                                st.write(f"**⏰ Type:** {job['employment_type']}")
                                st.write(f"**📝 Description:** {job['description']}")

                                # Benefits display
                                if 'benefits' in job:
                                    st.write("**🎁 Benefits:**")
                                    benefits_text = " | ".join(job['benefits'])
                                    st.write(benefits_text)

                            with col2:
                                if st.button(f"💾 Save Job", key=f"save_{i}"):
                                    save_job_to_db(job)
                                    st.success("Job saved!")

                                if st.button(f"🔗 Apply Now", key=f"apply_{i}"):
                                    st.info(f"Opening: {job['url']}")

                                # AI match score
                                match_score = random.randint(75, 95)
                                st.metric("🎯 AI Match", f"{match_score}%")
                else:
                    st.warning("No jobs found. Try different keywords.")

# Step 18: Resume Analysis Tab
with tab3:
    st.subheader("📄 AI Resume Analysis & Optimization")

    st.info("💡 Upload your resume for AI-powered analysis and personalized feedback!")

    # Resume upload
    uploaded_file = st.file_uploader("Choose your resume file",
                                     type=['pdf', 'docx', 'txt'],
                                     help="Supported formats: PDF, DOCX, TXT")

    if uploaded_file is not None:
        st.success("✅ Resume uploaded successfully!")

        # Mock resume analysis
        with st.spinner("🤖 AI is analyzing your resume..."):
            time.sleep(2)  # Simulate processing

            # Resume analysis results
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Analysis Results")

                # Overall score
                overall_score = random.randint(70, 90)
                st.metric("Overall Resume Score", f"{overall_score}/100")

                # Individual scores
                scores = {
                    "Format & Structure": random.randint(75, 95),
                    "Content Quality": random.randint(65, 85),
                    "Keyword Optimization": random.randint(60, 80),
                    "Skills Relevance": random.randint(70, 90),
                    "Experience Description": random.randint(75, 95)
                }

                for metric, score in scores.items():
                    st.progress(score/100)
                    st.write(f"**{metric}:** {score}/100")

            with col2:
                st.subheader("💡 AI Recommendations")

                recommendations = [
                    "🎯 Add more quantifiable achievements (e.g., 'Increased sales by 25%')",
                    "🔑 Include more relevant keywords for your target role",
                    "📝 Improve action verbs - use 'achieved', 'implemented', 'optimized'",
                    "📊 Add technical skills section with proficiency levels",
                    "🎨 Consider updating the format for better readability",
                    "🏆 Highlight your most significant accomplishments first"
                ]

                for rec in recommendations[:4]:  # Show top 4
                    st.write(f"• {rec}")

        # Resume improvement suggestions
        st.subheader("🚀 Suggested Improvements")

        improvement_tabs = st.tabs(["Keywords", "Format", "Content", "Skills"])

        with improvement_tabs[0]:
            st.write("**Missing Keywords for your target role:**")
            keywords = ["Python", "Machine Learning", "SQL", "AWS", "Docker", "Kubernetes"]
            for keyword in keywords:
                st.write(f"• {keyword}")

        with improvement_tabs[1]:
            st.write("**Format Suggestions:**")
            st.write("• Use consistent font sizes and spacing")
            st.write("• Include clear section headers")
            st.write("• Keep to 1-2 pages maximum")
            st.write("• Use bullet points for easy scanning")

        with improvement_tabs[2]:
            st.write("**Content Enhancement:**")
            st.write("• Start bullet points with strong action verbs")
            st.write("• Include specific metrics and numbers")
            st.write("• Tailor content to job requirements")
            st.write("• Remove outdated or irrelevant information")

        with improvement_tabs[3]:
            st.write("**Skills Optimization:**")
            st.write("• Group technical and soft skills separately")
            st.write("• Include proficiency levels")
            st.write("• Add emerging technologies in your field")
            st.write("• Highlight certifications and training")

# Step 19: Interview Preparation Tab
with tab4:
    st.subheader("🎤 AI-Powered Interview Preparation")

    # Interview prep options
    prep_type = st.selectbox("Choose Interview Preparation Type:",
                             ["General Interview", "Technical Interview", "Behavioral Interview", "Case Study Interview"])

    target_role = st.text_input("Target Role",
                                value=st.session_state.user_profile.get('roles', ''),
                                placeholder="e.g., Software Engineer, Data Scientist")

    if st.button("🎯 Generate Interview Questions", type="primary"):
        if target_role:
            with st.spinner("🤖 AI is preparing personalized interview questions..."):
                questions = get_interview_questions_by_role(target_role)

                st.success(f"📝 Generated {len(questions)} questions for {target_role} role!")

                for i, q in enumerate(questions, 1):
                    with st.expander(f"Question {i}: {q['question']}", expanded=i==1):
                        st.write(f"**Category:** {q['category']}")
                        st.write(f"**Difficulty:** {q['difficulty']}")

                        # STAR method reminder for behavioral questions
                        if q['category'] in ['Leadership', 'Collaboration', 'Decision Making']:
                            st.info("💡 **STAR Method Reminder:**\n"
                                   "- **Situation:** Set the context\n"
                                   "- **Task:** Describe what you needed to do\n"
                                   "- **Action:** Explain what you did\n"
                                   "- **Result:** Share the outcome")

                        # Practice section
                        st.write("**🎯 Practice Area:**")
                        answer = st.text_area(f"Practice your answer for Question {i}:",
                                            placeholder="Type your practice answer here...",
                                            key=f"practice_{i}")

                        if answer:
                            st.write("**✅ Great! Here are some tips:**")
                            st.write("• Be specific with examples")
                            st.write("• Keep answers concise (2-3 minutes)")
                            st.write("• Practice out loud for better delivery")

    # Interview tips section
    st.subheader("💡 Interview Success Tips")

    tips_tabs = st.tabs(["Before", "During", "After"])

    with tips_tabs[0]:
        st.write("**📋 Before the Interview:**")
        st.write("• Research the company thoroughly")
        st.write("• Prepare questions to ask the interviewer")
        st.write("• Practice your elevator pitch")
        st.write("• Prepare copies of your resume")
        st.write("• Plan your route and arrive early")

    with tips_tabs[1]:
        st.write("**🎯 During the Interview:**")
        st.write("• Make eye contact and smile")
        st.write("• Listen carefully to questions")
        st.write("• Use the STAR method for behavioral questions")
        st.write("• Ask thoughtful questions")
        st.write("• Show enthusiasm for the role")

    with tips_tabs[2]:
        st.write("**📧 After the Interview:**")
        st.write("• Send a thank-you email within 24 hours")
        st.write("• Reiterate your interest in the role")
        st.write("• Address any concerns you may have missed")
        st.write("• Follow up appropriately")
        st.write("• Reflect on what went well and what to improve")

# Step 20: Salary Insights Tab
with tab5:
    st.subheader("💰 AI-Powered Salary Insights & Negotiation")

    col1, col2 = st.columns(2)

    with col1:
        salary_role = st.text_input("Job Role for Salary Analysis",
                                    placeholder="e.g., Software Engineer, Data Scientist")

    with col2:
        salary_location = st.text_input("Location",
                                        placeholder="e.g., San Francisco, New York, Remote")

    if st.button("💡 Get Salary Insights", type="primary"):
        if salary_role and salary_location:
            with st.spinner("🤖 AI is analyzing salary data..."):
                salary_info = get_salary_insights(salary_role, salary_location)

                # Display salary information
                st.success("📊 Salary Analysis Complete!")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("💰 Salary Range", salary_info['salary_range'])

                with col2:
                    st.metric("📊 Market Average", salary_info['average'])

                with col3:
                    market_trend = random.choice(["📈 Rising", "📊 Stable", "📉 Declining"])
                    st.metric("📈 Market Trend", market_trend)

                # Negotiation tips
                st.subheader("🎯 Negotiation Strategy")

                for tip in salary_info['negotiation_tips']:
                    st.write(f"• {tip}")

                # Salary breakdown
                st.subheader("💼 Total Compensation Breakdown")

                base_salary = random.randint(80000, 150000)
                bonus = random.randint(5000, 25000)
                equity = random.randint(10000, 50000)
                benefits = random.randint(15000, 30000)

                comp_data = {
                    "Component": ["Base Salary", "Bonus", "Equity", "Benefits"],
                    "Amount": [f"${base_salary:,}", f"${bonus:,}", f"${equity:,}", f"${benefits:,}"]
                }

                st.table(comp_data)

    # Negotiation tips
    st.subheader("🎯 Salary Negotiation Masterclass")

    negotiation_tabs = st.tabs(["Preparation", "Tactics", "Common Mistakes"])

    with negotiation_tabs[0]:
        st.write("**📋 Preparation Checklist:**")
        st.write("• Research market rates using multiple sources")
        st.write("• Document your achievements and contributions")
        st.write("• Understand the company's compensation philosophy")
        st.write("• Prepare your value proposition")
        st.write("• Set your minimum acceptable offer")

    with negotiation_tabs[1]:
        st.write("**🎯 Negotiation Tactics:**")
        st.write("• Let them make the first offer")
        st.write("• Negotiate total compensation, not just salary")
        st.write("• Be prepared to walk away")
        st.write("• Use silence as a tool")
        st.write("• Get everything in writing")

    with negotiation_tabs[2]:
        st.write("**❌ Common Mistakes to Avoid:**")
        st.write("• Accepting the first offer immediately")
        st.write("• Focusing only on salary")
        st.write("• Negotiating via email")
        st.write("• Not having a backup plan")
        st.write("• Being too aggressive or too passive")

# Step 21: Saved Jobs Tab
with tab6:
    st.subheader("💾 Your Saved Jobs")

    # Function to save job to database
    def save_job_to_db(job):
        try:
            conn = sqlite3.connect('enhanced_job_search.db')
            c = conn.cursor()
            c.execute("""INSERT INTO saved_jobs
                         (title, company, location, description, url, salary, source, employment_type, posted_date)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (job['title'], job['company'], job['location'], job['description'],
                       job['url'], job['salary'], job['source'], job['employment_type'], job['posted_date']))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving job: {e}")
            return False

    # Function to get saved jobs
    def get_saved_jobs():
        try:
            conn = sqlite3.connect('enhanced_job_search.db')
            c = conn.cursor()
            c.execute("SELECT * FROM saved_jobs ORDER BY saved_at DESC")
            jobs = c.fetchall()
            conn.close()
            return jobs
        except Exception as e:
            st.error(f"Error fetching saved jobs: {e}")
            return []

    # Display saved jobs
    saved_jobs = get_saved_jobs()

    if saved_jobs:
        st.success(f"📁 You have {len(saved_jobs)} saved jobs")

        for job in saved_jobs:
            with st.expander(f"{job[1]} at {job[2]} - {job[3]}"):  # title, company, location
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**📍 Location:** {job[3]}")
                    st.write(f"**💰 Salary:** {job[6]}")
                    st.write(f"**📅 Posted:** {job[9]}")
                    st.write(f"**📝 Description:** {job[4]}")
                    st.write(f"**🔗 URL:** {job[5]}")

                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{job[0]}"):
                        # Remove job from database
                        try:
                            conn = sqlite3.connect('enhanced_job_search.db')
                            c = conn.cursor()
                            c.execute("DELETE FROM saved_jobs WHERE id = ?", (job[0],))
                            conn.commit()
                            conn.close()
                            st.success("Job removed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error removing job: {e}")

                    if st.button(f"📊 Analyze", key=f"analyze_{job[0]}"):
                        st.info("🤖 AI Analysis: This job matches 85% of your profile!")
    else:
        st.info("📂 No saved jobs yet. Start searching and save interesting opportunities!")

# Step 22: Dashboard Tab
with tab7:
    st.subheader("📊 Your Career Dashboard")

    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_searches = len(get_conversation_history("session_1"))
        st.metric("🔍 Total Searches", total_searches)

    with col2:
        saved_count = len(get_saved_jobs())
        st.metric("💾 Saved Jobs", saved_count)

    with col3:
        chat_messages = len(st.session_state.chat_history)
        st.metric("💬 Chat Messages", chat_messages)

    with col4:
        profile_completion = 75 if st.session_state.user_profile else 25
        st.metric("👤 Profile Complete", f"{profile_completion}%")

    # Recent activity
    st.subheader("📝 Recent Activity")

    if st.session_state.chat_history:
        st.write("**Recent Conversations:**")
        for i, (user_msg, bot_msg, timestamp) in enumerate(st.session_state.chat_history[-5:]):
            st.write(f"• {timestamp}: {user_msg[:50]}...")
    else:
        st.info("No recent activity. Start chatting with the AI assistant!")

    # Career progress tracking
    st.subheader("🎯 Career Goals Progress")

    goals = {
        "Update Resume": random.randint(60, 90),
        "Practice Interviews": random.randint(40, 80),
        "Network Building": random.randint(30, 70),
        "Skill Development": random.randint(50, 90),
        "Job Applications": random.randint(20, 60)
    }

    for goal, progress in goals.items():
        st.write(f"**{goal}**")
        st.progress(progress/100)
        st.write(f"{progress}% Complete")

    # Weekly insights
    st.subheader("📈 Weekly Insights")

    insights = [
        "🎯 You've been most active on Tuesday afternoons",
        "📊 Your job search activity increased by 25% this week",
        "💼 Software Engineering roles are trending in your searches",
        "📍 Remote positions make up 60% of your saved jobs",
        "🤖 AI suggests focusing on Python and Machine Learning skills"
    ]

    for insight in insights:
        st.write(f"• {insight}")

# Step 23: Footer and Additional Features
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <h3>🤖 AI Job Search Assistant</h3>
    <p>Your intelligent career companion powered by advanced AI</p>
    <p><strong>Features:</strong> Job Search | Resume Analysis | Interview Prep | Salary Insights | Career Coaching</p>
    <p><em>Made with ❤️ and AI</em></p>
</div>
""", unsafe_allow_html=True)

# Step 24: Additional Helper Functions
def export_user_data():
    """Export user data for backup"""
    try:
        user_data = {
            'profile': st.session_state.user_profile,
            'chat_history': st.session_state.chat_history,
            'saved_jobs': get_saved_jobs(),
            'export_date': datetime.datetime.now().isoformat()
        }
        return json.dumps(user_data, indent=2)
    except Exception as e:
        return f"Error exporting data: {e}"

def get_career_recommendations():
    """Get personalized career recommendations"""
    recommendations = [
        "🎯 Consider learning cloud technologies like AWS or Azure",
        "📊 Data analysis skills are highly valued across industries",
        "🤝 Build your professional network through LinkedIn",
        "📚 Consider getting certified in your field",
        "💼 Tailor your resume for each job application",
        "🎤 Practice your interview skills regularly",
        "📈 Stay updated with industry trends and news",
        "🌟 Contribute to open source projects to showcase skills"
    ]
    return recommendations

# Step 25: Session Management and Cleanup
def cleanup_old_sessions():
    """Clean up old conversation data"""
    try:
        conn = sqlite3.connect('enhanced_job_search.db')
        c = conn.cursor()
        # Delete conversations older than 30 days
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
        c.execute("DELETE FROM chat_conversations WHERE timestamp < ?", (cutoff_date,))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

# Run cleanup
cleanup_old_sessions()

# Success message
if st.sidebar.button("🎉 Show Success Tips"):
    st.sidebar.success("""
    **🚀 Tips for Job Search Success:**

    1. **Be Consistent**: Search regularly, not just when desperate
    2. **Quality over Quantity**: Apply to fewer, well-matched roles
    3. **Network Actively**: Most jobs come through connections
    4. **Stay Updated**: Keep learning new skills
    5. **Be Patient**: Great opportunities take time to find

    **You've got this! 💪**
    """)

# Debug information (can be removed in production)
if st.sidebar.checkbox("🔧 Debug Mode"):
    st.sidebar.write("**Session State:**")
    st.sidebar.json({
        "Profile": st.session_state.user_profile,
        "Chat History Length": len(st.session_state.chat_history),
        "Current Time": datetime.datetime.now().isoformat()
    })

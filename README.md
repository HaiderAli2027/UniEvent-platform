UniEvent: Campus Event Discovery Platform

"Every Event. One Platform." UniEvent is a high-performance web application designed to centralize campus life. It eliminates the "poster-scatter" problem by providing a single source of truth for students to find events and for societies to grow their community.

The Problem:
Campus engagement is currently fragmented. Information is buried in WhatsApp groups, Instagram stories, and physical notice boards.

1. Students miss out on opportunities because they don't see them in time.
2. Societies struggle to reach beyond their existing follower base.
3. Data on event engagement (likes, views, attendance) is almost non-existent.

The Solution
UniEvent provides a centralized dashboard where:

1. Students can discover, like, and comment on events in a modern, interactive feed.
2. Societies can register, get verified, and manage their events through a professional Command Center.
3. Admins oversee the ecosystem to ensure quality and security.

Technical Architecture
Frontend (The Experience)

1. Modern UI: Built with Tailwind CSS for a "glassmorphic" and responsive design.
2. Interactive UX: \* 3D Login: A mouse-tracking 3D parallax effect on the login card
3. Dynamic Typing: Hero section typing effects for a premium feel.
4. Live Dashboard: Real-time role switching between Admin and Society views.
5. Technologies: HTML5, JavaScript (ES6+), FontAwesome.

Backend (The Core)

1. Framework: Flask (Python) with a modular Blueprint structure.
2. Database: SQLAlchemy (SQLite) featuring complex relationships (Many-to-Many for Event Likes).
3. Security: Role-Based Access Control (RBAC), password hashing with Werkzeug, and frontend-gatekeeping logic.
4. API: RESTful architecture serving JSON data to a decoupled frontend.

Key Features

1. Interactive Event Feed
   Real-time Interaction: Users can "Interest" (Like) events, which updates the database instantly.
   Social Connectivity: Direct links to Instagram, WhatsApp, and Google Registration Forms.
   Filter Logic: Sort events by category (Workshops, Socials, Competitions).

2. Society Command Center
   Event Publisher: Professional interface to upload posters, venues, and descriptions.
   Analytics: View stats on how many students have engaged with specific events.
   Verification Status: Societies can track their approval status from the university.

3. Role-Based Access Control (RBAC)
   Student: Can view, search, and engage.
   Society: Access to the Management Dashboard once verified.
   Admin: Full system oversight, including society verification and event moderation.

Challenges Overcome:

1. Managing the state of the 3D parallax effect while handling real-time form validation in login-signup.js.
2. Relationship Mapping: Implementing a Many-to-Many relationship in SQLAlchemy to track "User Likes" across hundreds of events efficiently.
3. Security Gatekeeping: Implementing checkAdminAccess() on the frontend to ensure society/admin dashboards are invisible to standard student accounts.

Future Roadmap

1. Push Notifications: Instant alerts when a "followed" society posts a new event.
2. QR Check-in: Generating unique QR codes for event attendance tracking.
3. In-App Chat: Allowing students to message society leads directly for inquiries.

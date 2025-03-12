'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/store';
import Link from 'next/link';
import { LeaderboardEntry } from '@/components/LeaderboardEntry';
import './styles.css';

// Sample data for demonstration
const sampleUsers = [
  { id: '1', name: 'John Doe', email: 'john@example.com', streak: 15, checkins: 45, events: 8 },
  { id: '2', name: 'Jane Smith', email: 'jane@example.com', streak: 12, checkins: 36, events: 6 },
  { id: '3', name: 'Alex Johnson', email: 'alex@example.com', streak: 10, checkins: 30, events: 5 },
  { id: '4', name: 'Sarah Williams', email: 'sarah@example.com', streak: 8, checkins: 24, events: 4 },
  { id: '5', name: 'Michael Brown', email: 'michael@example.com', streak: 7, checkins: 21, events: 3 },
];

// Sample event data for demonstration
const sampleEvents = [
  { 
    id: '1', 
    name: 'Annual Tech Conference', 
    description: 'Join us for the biggest tech event of the year with industry leaders and innovators.',
    date: '2023-12-15',
    location: 'San Francisco, CA',
    participants: 120,
    isJoined: true
  },
  { 
    id: '2', 
    name: 'Web Development Workshop', 
    description: 'Learn the latest web development techniques and tools in this hands-on workshop.',
    date: '2023-11-20',
    location: 'Online',
    participants: 85,
    isJoined: false
  },
  { 
    id: '3', 
    name: 'AI in Healthcare Symposium', 
    description: 'Explore how artificial intelligence is transforming healthcare delivery and research.',
    date: '2024-01-10',
    location: 'Boston, MA',
    participants: 95,
    isJoined: true
  },
  { 
    id: '4', 
    name: 'Mobile App Design Masterclass', 
    description: 'Master the art of creating beautiful and functional mobile app interfaces.',
    date: '2023-12-05',
    location: 'New York, NY',
    participants: 60,
    isJoined: false
  },
  { 
    id: '5', 
    name: 'Cybersecurity Summit', 
    description: 'Stay ahead of threats with insights from top cybersecurity experts.',
    date: '2024-02-20',
    location: 'Washington, DC',
    participants: 110,
    isJoined: false
  },
];

export default function DashboardPage() {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const router = useRouter();

  // Authentication check temporarily disabled
  // useEffect(() => {
  //   if (!isAuthenticated) {
  //     router.push('/auth/login');
  //   }
  // }, [isAuthenticated, router]);

  // Provide default user experience when no user data is available
  const userName = user?.name || 'Guest';
  
  // Get user initials for avatar
  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };
  
  // No longer blocking rendering when user is null

  return (
    <main className="dashboard-container">
      <div className="dashboard-content">
        {/* Welcome Header */}
        <div className="welcome-header">
          <h1 className="welcome-title">Welcome, {userName}!</h1>
          <p className="welcome-subtitle">Manage your attendance and events from your dashboard</p>
        </div>

        {/* Quick Actions */}
        <div className="section-container">
          <h2 className="section-title">Quick Actions</h2>
          <div className="quick-actions-grid">
            <Link href="/checkin/today" className="action-card checkin-card">
              <h3 className="action-card-title">Today's Check-in</h3>
              <p>Mark your attendance for today</p>
            </Link>
            <Link href="/events" className="action-card events-card">
              <h3 className="action-card-title">Events</h3>
              <p>View and manage your events</p>
            </Link>
            <Link href="/user/profile" className="action-card profile-card">
              <h3 className="action-card-title">Profile</h3>
              <p>Update your profile information</p>
            </Link>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="section-container">
          <h2 className="section-title">Your Stats</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <p className="stat-label">Current Streak</p>
              <p className="stat-value streak-value">0 days</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Longest Streak</p>
              <p className="stat-value longest-streak-value">0 days</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Total Check-ins</p>
              <p className="stat-value checkins-value">0</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Events Joined</p>
              <p className="stat-value events-value">0</p>
            </div>
          </div>
        </div>

        {/* Leaderboard Preview */}
        <div className="section-container">
          <div className="leaderboard-header">
            <h2 className="section-title">Leaderboard</h2>
            <Link href="/user/leaderboard" className="view-all-link">
              View Full Leaderboard
            </Link>
          </div>
          <div className="leaderboard-card">
            {sampleUsers && sampleUsers.length > 0 ? (
              <table className="leaderboard-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>User</th>
                    <th>Streak</th>
                  </tr>
                </thead>
                <tbody>
                  {sampleUsers.slice(0, 3).map((user, index) => {
                    const rank = index + 1;
                    return (
                      <LeaderboardEntry 
                        key={user.id}
                        user={user}
                        rank={rank}
                        showDetails={false}
                      />
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <div className="leaderboard-empty">
                Join events and maintain your streak to appear on the leaderboard!
              </div>
            )}
          </div>
        </div>

        {/* Popular Events Section */}
        <div className="section-container">
          <div className="leaderboard-header">
            <h2 className="section-title">Popular Events</h2>
            <Link href="/events" className="view-all-link">
              View All Events
            </Link>
          </div>
          <div className="events-preview-grid">
            {sampleEvents
              .sort((a, b) => b.participants - a.participants)
              .slice(0, 3)
              .map((event) => (
                <div key={event.id} className="event-preview-card">
                  <div className="event-preview-header">
                    <h3 className="event-preview-title">{event.name}</h3>
                    <span className="event-preview-date">
                      {new Date(event.date).toLocaleDateString(undefined, { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </span>
                  </div>
                  <p className="event-preview-description">{event.description}</p>
                  <div className="event-preview-footer">
                    <div className="event-preview-participants">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                      </svg>
                      <span>{event.participants} participants</span>
                    </div>
                    <Link href={`/events/${event.id}`} className="event-preview-link">
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* My Events Section */}
        <div className="section-container">
          <div className="leaderboard-header">
            <h2 className="section-title">My Events</h2>
            <Link href="/events" className="view-all-link">
              View All Events
            </Link>
          </div>
          <div className="events-preview-grid">
            {sampleEvents
              .filter(event => event.isJoined)
              .slice(0, 3)
              .map((event) => (
                <div key={event.id} className="event-preview-card">
                  <div className="event-preview-header">
                    <h3 className="event-preview-title">{event.name}</h3>
                    <span className="event-preview-date">
                      {new Date(event.date).toLocaleDateString(undefined, { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </span>
                  </div>
                  <p className="event-preview-description">{event.description}</p>
                  <div className="event-preview-footer">
                    <div className="event-preview-location">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                      </svg>
                      <span>{event.location}</span>
                    </div>
                    <Link href={`/events/${event.id}`} className="event-preview-link">
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
            {sampleEvents.filter(event => event.isJoined).length === 0 && (
              <div className="no-events-message">
                <p>You haven't joined any events yet.</p>
                <Link href="/events" className="browse-events-link">
                  Browse Events
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
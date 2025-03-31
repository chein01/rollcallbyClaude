'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/store';
import Link from 'next/link';
import { LeaderboardEntry } from '@/components/LeaderboardEntry';
import { EventCard } from '@/components/EventCard';
import './styles.css';
import { Calendar, User, Settings, Star, MapPin, Users, LineChart, Award } from 'lucide-react';
import { Event, EventStatus } from '@/types/event';
import { EventGroup } from '@/components/EventGroup';
import { MiniCalendar } from '@/components/MiniCalendar';
import { CheckInBanner } from '@/components/CheckInBanner';

// Sample data for demonstration
const sampleUsers = [
  { id: '1', name: 'John Doe', email: 'john@example.com', streak: 15, checkins: 45, events: 8 },
  { id: '2', name: 'Jane Smith', email: 'jane@example.com', streak: 12, checkins: 36, events: 6 },
  { id: '3', name: 'Alex Johnson', email: 'alex@example.com', streak: 10, checkins: 30, events: 5 },
  { id: '4', name: 'Sarah Williams', email: 'sarah@example.com', streak: 8, checkins: 24, events: 4 },
  { id: '5', name: 'Michael Brown', email: 'michael@example.com', streak: 7, checkins: 21, events: 3 },
];

// Sample event data for demonstration
const sampleEvents: Event[] = [
  {
    id: '1',
    title: 'Annual Tech Conference',
    description: 'Join us for the biggest tech event of the year with industry leaders and innovators.',
    startDate: new Date(new Date().setHours(9, 0, 0, 0)).toISOString(), // Set to 9:00 AM today
    endDate: new Date(new Date().setHours(17, 0, 0, 0)).toISOString(), // Set to 5:00 PM today
    location: 'San Francisco, CA',
    participants: 120,
    stars: 45,
    status: 'ongoing' as EventStatus,
    hasJoined: true,
    isCheckedIn: false
  },
  {
    id: '2',
    title: 'Web Development Workshop',
    description: 'Learn the latest web development techniques and tools in this hands-on workshop.',
    startDate: new Date(new Date().setHours(14, 0, 0, 0)).toISOString(), // Set to 2:00 PM today
    endDate: new Date(new Date().setHours(17, 0, 0, 0)).toISOString(), // Set to 5:00 PM today
    location: 'Online',
    participants: 85,
    stars: 32,
    status: 'ongoing' as EventStatus,
    hasJoined: true,
    isCheckedIn: false
  },
  {
    id: '3',
    title: 'AI in Healthcare Symposium',
    description: 'Explore how artificial intelligence is transforming healthcare delivery and research.',
    startDate: new Date(new Date(Date.now() + 24 * 60 * 60 * 1000).setHours(10, 0, 0, 0)).toISOString(), // Tomorrow 10:00 AM
    endDate: new Date(new Date(Date.now() + 24 * 60 * 60 * 1000).setHours(16, 0, 0, 0)).toISOString(), // Tomorrow 4:00 PM
    location: 'Boston, MA',
    participants: 95,
    stars: 38,
    status: 'ongoing' as EventStatus,
    hasJoined: true,
    isCheckedIn: false
  }
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

  const handleCheckIn = async (eventId: string) => {
    // Giả lập API call
    const updatedEvents = sampleEvents.map(event =>
      event.id === eventId
        ? { ...event, isCheckedIn: true }
        : event
    );
    console.log('Checked in for event:', eventId);
  };

  return (
    <main className="dashboard-container">
      <div className="dashboard-content">
        {/* Welcome Header */}
        <div className="welcome-header">
          <h1 className="welcome-title">Welcome, {userName}!</h1>
          <p className="welcome-subtitle">Manage your attendance and events from your dashboard</p>
          <CheckInBanner events={sampleEvents} />
        </div>

        {/* Overview Grid */}
        <div className="overview-grid">
          <div className="overview-main">
            {/* Events and Calendar Section */}
            <div className="section-container">
              <h2 className="section-title">Events Overview</h2>
              <div className="events-overview-grid">
                <div className="events-section">
                  <EventGroup
                    events={sampleEvents}
                    onStarClick={async (eventId) => {
                      console.log('Star clicked for event:', eventId);
                    }}
                    onCheckIn={handleCheckIn}
                  />
                </div>
                <div className="calendar-section">
                  <MiniCalendar events={sampleEvents} />
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="section-container">
              <h2 className="section-title">Quick Actions</h2>
              <div className="quick-actions-grid">
                <Link href="/analytics" className="action-card action-card-analytics">
                  <div className="action-card-icon">
                    <LineChart className="h-5 w-5" />
                  </div>
                  <h3 className="action-card-title">Analytics</h3>
                  <p>Check your attendance stats</p>
                </Link>
                <Link href="/achievements" className="action-card action-card-streak">
                  <div className="action-card-icon">
                    <Award className="h-5 w-5" />
                  </div>
                  <h3 className="action-card-title">Achievements</h3>
                  <p>View your badges and rewards</p>
                </Link>
                <Link href="/user/profile" className="action-card action-card-profile">
                  <div className="action-card-icon">
                    <User className="h-5 w-5" />
                  </div>
                  <h3 className="action-card-title">Profile</h3>
                  <p>Update your information</p>
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
              <p className="no-data-message">No leaderboard data available</p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
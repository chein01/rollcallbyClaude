'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/store';
import Link from 'next/link';
import { LeaderboardEntry } from '@/components/LeaderboardEntry';
import { EventCard } from '@/components/EventCard';
import './styles.css';
import { Calendar, User, Settings, Star, MapPin, Users, LineChart, Award, CheckCircle } from 'lucide-react';
import { Event, EventStatus } from '@/types/event';
import { EventGroup } from '@/components/EventGroup';
import { MiniCalendar } from '@/components/MiniCalendar';
import { CheckInBanner } from '@/components/CheckInBanner';
import { PriorityEventView } from '@/components/PriorityEventView';
import { isToday, isFuture, isPast, isThisWeek } from 'date-fns';

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
  const userName = user?.name || 'Guest';

  // State for events after check-in
  const [events, setEvents] = useState<Event[]>(sampleEvents);
  const [lastCheckedInEvent, setLastCheckedInEvent] = useState<Event | undefined>();
  const [showBanner, setShowBanner] = useState<boolean>(true);

  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  const handleCheckIn = async (eventId: string) => {
    try {
      // Find the event that was checked in
      const checkedEvent = events.find(event => event.id === eventId);

      // Update the event's check-in status
      if (checkedEvent) {
        checkedEvent.isCheckedIn = true;
        setLastCheckedInEvent(checkedEvent);
        setShowBanner(true); // Ensure banner is shown when there's a new check-in
      }

      // Update the events list
      setEvents([...events]);
    } catch (error) {
      console.error('Error checking in:', error);
    }
  };

  const handleCloseBanner = () => {
    setShowBanner(false);
    setLastCheckedInEvent(undefined);
  };

  // Filter functions for events
  const isTodayEvent = (event: Event) => {
    return isToday(new Date(event.startDate));
  };

  const isUpcomingEvent = (event: Event) => {
    return isFuture(new Date(event.startDate)) && !isToday(new Date(event.startDate));
  };

  return (
    <main className="dashboard-container">
      <div className="dashboard-content">
        {/* Welcome Header */}
        <div className="welcome-header">
          <h1 className="welcome-title">Welcome, {userName}!</h1>
          <p className="welcome-subtitle">Manage your attendance and events from your dashboard</p>
          {showBanner && (
            <CheckInBanner
              pendingEvents={events.filter(event => !event.isCheckedIn)}
              onClose={handleCloseBanner}
              lastCheckedInEvent={lastCheckedInEvent}
            />
          )}
        </div>

        {/* Events Overview - Redesigned for Priority View */}
        <div className="section-container">
          <h2 className="section-title">Events Overview</h2>
          <div className="events-overview-grid">
            {/* Today's Events - Priority View */}
            <PriorityEventView
              events={events}
              title="Today's Events"
              emptyMessage="All tasks completed for today"
              onCheckIn={handleCheckIn}
              onStarClick={(eventId) => console.log('Star clicked:', eventId)}
              filter={isTodayEvent}
            />

            {/* Upcoming Events - Priority View */}
            <PriorityEventView
              events={events}
              title="Upcoming Events"
              emptyMessage="No upcoming events"
              onCheckIn={handleCheckIn}
              onStarClick={(eventId) => console.log('Star clicked:', eventId)}
              filter={isUpcomingEvent}
            />
          </div>
        </div>

        {/* Mini Calendar */}
        <div className="section-container">
          <MiniCalendar events={events} />
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

        {/* Leaderboard Preview */}
        <div className="section-container">
          <div className="leaderboard-header">
            <h2 className="section-title">Leaderboard</h2>
            <Link href="/user/leaderboard" className="view-all-link">
              View Full Leaderboard
            </Link>
          </div>

          <div className="leaderboard-dashboard-card">
            {sampleUsers && sampleUsers.length > 0 ? (
              <div className="leaderboard-top-users">
                {/* Top 3 users with medal styling */}
                {sampleUsers.slice(0, 3).map((user, index) => {
                  const rank = index + 1;
                  const rankIcon = rank === 1 ? '👑' : rank === 2 ? '🥈' : '🥉';

                  return (
                    <div key={user.id} className={`top-user-card rank-${rank}`}>
                      <div className="medal-badge">
                        <div className={`medal ${rank === 1 ? 'gold' : rank === 2 ? 'silver' : 'bronze'}`}>
                          {rankIcon}
                        </div>
                      </div>
                      <div className="user-avatar-container">
                        <div className={`user-avatar-large ${rank === 1 ? 'gold-bg' : rank === 2 ? 'silver-bg' : 'bronze-bg'}`}>
                          {getUserInitials(user.name)}
                        </div>
                      </div>
                      <div className="user-info">
                        <h3 className="user-name">{user.name}</h3>
                        <p className="user-streak">{user.streak} days streak</p>
                        <div className="user-stats">
                          <span className="stat"><CheckCircle size={14} className="inline mr-1" /> {user.checkins} check-ins</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="no-data-message">No leaderboard data available</p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
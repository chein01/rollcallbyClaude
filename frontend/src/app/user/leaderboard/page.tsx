'use client';

import { useState } from 'react';
import { useAppSelector } from '@/store';
import Link from 'next/link';
import { LeaderboardEntry } from '@/components/LeaderboardEntry';
import './styles.css';

interface LeaderboardUser {
  id: string;
  name: string;
  email: string;
  streak: number;
  checkins: number;
  events: number;
}

// Sample data for demonstration - expanded to 100 users
const generateSampleUsers = (): LeaderboardUser[] => {
  const users: LeaderboardUser[] = [
    { id: '1', name: 'John Doe', email: 'john@example.com', streak: 15, checkins: 45, events: 8 },
    { id: '2', name: 'Jane Smith', email: 'jane@example.com', streak: 12, checkins: 36, events: 6 },
    { id: '3', name: 'Alex Johnson', email: 'alex@example.com', streak: 10, checkins: 30, events: 5 },
    { id: '4', name: 'Sarah Williams', email: 'sarah@example.com', streak: 8, checkins: 24, events: 4 },
    { id: '5', name: 'Michael Brown', email: 'michael@example.com', streak: 7, checkins: 21, events: 3 },
    { id: '6', name: 'Emily Davis', email: 'emily@example.com', streak: 6, checkins: 18, events: 3 },
    { id: '7', name: 'David Miller', email: 'david@example.com', streak: 5, checkins: 15, events: 2 },
    { id: '8', name: 'Lisa Wilson', email: 'lisa@example.com', streak: 4, checkins: 12, events: 2 },
    { id: '9', name: 'Robert Taylor', email: 'robert@example.com', streak: 3, checkins: 9, events: 1 },
    { id: '10', name: 'Jennifer Moore', email: 'jennifer@example.com', streak: 2, checkins: 6, events: 1 },
  ];
  
  // Generate additional users to reach 100
  for (let i = 11; i <= 100; i++) {
    users.push({
      id: i.toString(),
      name: `User ${i}`,
      email: `user${i}@example.com`,
      streak: Math.max(1, Math.floor(Math.random() * 15)),
      checkins: Math.floor(Math.random() * 50),
      events: Math.floor(Math.random() * 10)
    });
  }
  
  return users;
};

const sampleUsers: LeaderboardUser[] = generateSampleUsers();

export default function LeaderboardPage() {
  const { user } = useAppSelector((state) => state.auth);
  const [timeFrame, setTimeFrame] = useState('all-time');
  const [sortBy, setSortBy] = useState('streak');
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  // Filter and sort users based on selected options
  const filteredUsers = [...sampleUsers].sort((a, b) => {
    if (sortBy === 'streak') return b.streak - a.streak;
    if (sortBy === 'checkins') return b.checkins - a.checkins;
    if (sortBy === 'events') return b.events - a.events;
    return 0;
  });

  // Pagination
  const indexOfLastUser = currentPage * rowsPerPage;
  const indexOfFirstUser = indexOfLastUser - rowsPerPage;
  const currentUsers = filteredUsers.slice(indexOfFirstUser, indexOfLastUser);
  const totalPages = Math.ceil(filteredUsers.length / rowsPerPage);
  
  // Handle rows per page change
  const handleRowsPerPageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRowsPerPage(Number(e.target.value));
    setCurrentPage(1); // Reset to first page when changing rows per page
  };

  // User initials are now handled by the LeaderboardEntry component

  return (
    <main className="leaderboard-container">
      <div className="leaderboard-content">
        {/* Page Header */}
        <div className="page-header">
          <h1 className="page-title">Leaderboard</h1>
          <p className="page-subtitle">See how you rank among other users</p>
        </div>

        {/* Filters */}
        <div className="filters-container">
          <div>
            <span className="filter-label">Time Frame:</span>
            <select
              className="filter-select"
              value={timeFrame}
              onChange={(e) => setTimeFrame(e.target.value)}
            >
              <option value="all-time">All Time</option>
              <option value="this-month">This Month</option>
              <option value="this-week">This Week</option>
            </select>
          </div>
          <div>
            <span className="filter-label">Sort By:</span>
            <select
              className="filter-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="streak">Streak</option>
              <option value="checkins">Check-ins</option>
              <option value="events">Events</option>
            </select>
          </div>
          <div>
            <span className="filter-label">Rows Per Page:</span>
            <select
              className="filter-select"
              value={rowsPerPage}
              onChange={handleRowsPerPageChange}
            >
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="leaderboard-table-container">
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>User</th>
                <th>Streak</th>
                <th>Check-ins</th>
                <th>Events</th>
              </tr>
            </thead>
            <tbody>
              {currentUsers.map((user, index) => {
                const rank = indexOfFirstUser + index + 1;
                return (
                  <LeaderboardEntry 
                    key={user.id}
                    user={user}
                    rank={rank}
                    showDetails={true}
                  />
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="pagination-button"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                className={`pagination-button ${currentPage === page ? 'active' : ''}`}
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </button>
            ))}
            <button
              className="pagination-button"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        )}

        {/* Back to Dashboard */}
        <div className="mt-8 text-center">
          <Link href="/dashboard" className="view-all-link">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}
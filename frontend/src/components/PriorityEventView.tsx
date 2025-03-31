'use client';

import React, { useState, useEffect } from 'react';
import { Event } from '@/types/event';
import { EventCard } from './EventCard';
import { CheckCircle, Calendar } from 'lucide-react';
import { CompletionConfetti } from './CompletionConfetti';

interface PriorityEventViewProps {
    events: Event[];
    title: string;
    emptyMessage?: string;
    onCheckIn?: (eventId: string) => void;
    onStarClick?: (eventId: string) => void;
    filter?: (event: Event) => boolean;
}

export function PriorityEventView({
    events,
    title,
    emptyMessage = "You have completed all check-in tasks for today",
    onCheckIn,
    onStarClick,
    filter = () => true
}: PriorityEventViewProps) {
    // Thêm state để xác định khi component đã mounted trên client
    const [isMounted, setIsMounted] = useState(false);
    // Thêm state để theo dõi số lượng check-in đã hoàn thành
    const [completedCheckIns, setCompletedCheckIns] = useState(0);
    // State để hiển thị confetti khi hoàn thành
    const [showConfetti, setShowConfetti] = useState(false);

    // Filter events and sort by start date
    const filteredEvents = events
        .filter(filter)
        .filter(event => !event.isCheckedIn)
        .sort((a, b) => new Date(a.startDate).getTime() - new Date(b.startDate).getTime());

    // State to track the currently displayed event
    const [currentEventIndex, setCurrentEventIndex] = useState(0);
    const [showCompleted, setShowCompleted] = useState(filteredEvents.length === 0);
    const [isAnimating, setIsAnimating] = useState(false);

    // Kiểm tra xem event hiện tại có tồn tại không
    const hasValidCurrentEvent = filteredEvents.length > 0 && currentEventIndex < filteredEvents.length;
    const currentEvent = hasValidCurrentEvent ? filteredEvents[currentEventIndex] : undefined;

    // Tính toán thành tích
    const getRandomAchievement = () => {
        const achievements = [
            "Attended 3/3 events this week",
            "+5 streak points! Keep it up",
            "Achievement: Professional Attendee",
            "Excellent completion!"
        ];
        return achievements[Math.floor(Math.random() * achievements.length)];
    };

    // Tạo gợi ý hành động tiếp theo
    const getRandomSuggestion = () => {
        const suggestions = [
            "Check upcoming events to plan ahead",
            "You're in the top 10% most active participants",
            "Don't forget you have 2 important events tomorrow",
            "Attend 3 more events to upgrade your badge"
        ];
        return suggestions[Math.floor(Math.random() * suggestions.length)];
    };

    // Handle check-in with simple fade effect
    const handleCheckIn = async (eventId: string) => {
        if (onCheckIn) {
            // Trigger the check-in
            await onCheckIn(eventId);

            // Tăng số lượng check-in đã hoàn thành
            setCompletedCheckIns(prev => prev + 1);

            // Start animation 
            setIsAnimating(true);

            // Update the displayed event after a short delay
            setTimeout(() => {
                // Nếu đây là event cuối cùng, hiển thị hiệu ứng confetti
                if (currentEventIndex >= filteredEvents.length - 1) {
                    setShowConfetti(true);
                    setShowCompleted(true);
                } else {
                    setCurrentEventIndex(prev => prev + 1);
                }
                // End animation
                setIsAnimating(false);
            }, 300); // Short delay for visual effect
        }
    };

    // Gắn mounted effect để tránh lỗi hydration
    useEffect(() => {
        setIsMounted(true);

        // Nếu ban đầu đã hoàn thành tất cả các sự kiện, hiển thị confetti
        if (filteredEvents.length === 0) {
            setShowConfetti(true);
        }
    }, []);

    // Reset state when events change
    useEffect(() => {
        if (filteredEvents.length === 0) {
            setShowCompleted(true);
            if (completedCheckIns > 0) {
                setShowConfetti(true);
            }
        } else {
            setCurrentEventIndex(0);
            setShowCompleted(false);
        }
    }, [events, filter, filteredEvents.length, completedCheckIns]);

    // Nếu component chưa mounted, hiển thị phiên bản tối giản để tránh lỗi hydration
    if (!isMounted) {
        return (
            <div className="priority-event-container">
                <div className="priority-event-header">
                    <h3 className="priority-event-title">{title}</h3>
                </div>
                <div className="priority-event-loading">Loading...</div>
            </div>
        );
    }

    return (
        <div className="priority-event-container">
            <div className="priority-event-header">
                <h3 className="priority-event-title">{title}</h3>
            </div>

            <div className="priority-event-content" style={{
                opacity: isAnimating ? 0.5 : 1,
                transition: 'opacity 300ms ease-in-out',
                position: 'relative'
            }}>
                {showConfetti && <CompletionConfetti count={80} duration={3000} />}

                {showCompleted || !hasValidCurrentEvent ? (
                    <div className="completed-message">
                        <CheckCircle />
                        <p>{emptyMessage}</p>
                        <div className="achievement">
                            {getRandomAchievement()}
                        </div>
                        <div className="suggestion">
                            <Calendar className="h-4 w-4 inline-block mr-1" />
                            {getRandomSuggestion()}
                        </div>
                    </div>
                ) : (
                    <EventCard
                        event={currentEvent}
                        onCheckIn={handleCheckIn}
                        onStarClick={onStarClick}
                    />
                )}
            </div>
        </div>
    );
} 
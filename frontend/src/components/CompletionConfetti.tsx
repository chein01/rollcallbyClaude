'use client';

import React, { useEffect, useState } from 'react';
import styles from './Confetti.module.css';

interface ConfettiProps {
    count?: number;
    duration?: number;
}

export function CompletionConfetti({ count = 100, duration = 3000 }: ConfettiProps) {
    const [confetti, setConfetti] = useState<React.ReactNode[]>([]);
    const [active, setActive] = useState(true);

    useEffect(() => {
        // Tạo các phần tử confetti
        const items: React.ReactNode[] = [];
        const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

        for (let i = 0; i < count; i++) {
            const left = Math.random() * 100; // Vị trí theo chiều ngang
            const size = Math.floor(Math.random() * 10) + 5; // Kích thước ngẫu nhiên từ 5px đến 15px
            const duration = (Math.random() * 3) + 2; // Thời gian rơi từ 2-5s
            const delay = Math.random() * 0.5; // Độ trễ ngẫu nhiên
            const color = colors[Math.floor(Math.random() * colors.length)]; // Màu ngẫu nhiên
            const rotation = Math.random() * 360; // Góc xoay ngẫu nhiên

            items.push(
                <div
                    key={i}
                    className={styles.confetti}
                    style={{
                        left: `${left}%`,
                        width: `${size}px`,
                        height: `${size}px`,
                        backgroundColor: color,
                        animationDuration: `${duration}s`,
                        animationDelay: `${delay}s`,
                        transform: `rotate(${rotation}deg)`
                    }}
                />
            );
        }

        setConfetti(items);

        // Sau khoảng thời gian duration, tắt hiệu ứng
        const timer = setTimeout(() => {
            setActive(false);
        }, duration);

        return () => clearTimeout(timer);
    }, [count, duration]);

    if (!active) return null;

    return (
        <div className={styles.confettiContainer}>
            {confetti}
        </div>
    );
} 
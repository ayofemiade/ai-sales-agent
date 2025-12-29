'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface IntroContextType {
    showIntro: boolean;
    isChecking: boolean;
    setShowIntro: (show: boolean) => void;
    replayIntro: () => void;
}

const IntroContext = createContext<IntroContextType | undefined>(undefined);

export function IntroProvider({ children }: { children: React.ReactNode }) {
    const [showIntro, setShowIntro] = useState(false);
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        const hasSeen = sessionStorage.getItem('hasSeenIntro');
        if (!hasSeen) {
            setShowIntro(true);
        }
        setIsChecking(false);
    }, []);

    const handleSetShowIntro = (show: boolean) => {
        setShowIntro(show);
        if (!show) {
            sessionStorage.setItem('hasSeenIntro', 'true');
        }
    };

    const replayIntro = () => {
        sessionStorage.removeItem('hasSeenIntro');
        setShowIntro(true);
    };

    return (
        <IntroContext.Provider value={{ showIntro, isChecking, setShowIntro: handleSetShowIntro, replayIntro }}>
            {children}
        </IntroContext.Provider>
    );
}

export function useIntro() {
    const context = useContext(IntroContext);
    if (context === undefined) {
        throw new Error('useIntro must be used within an IntroProvider');
    }
    return context;
}

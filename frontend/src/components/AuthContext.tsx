'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { account } from '@/lib/appwrite';
import { Models, OAuthProvider } from 'appwrite';

interface AuthContextType {
    user: Models.User<Models.Preferences> | null;
    loading: boolean;
    isAuthModalOpen: boolean;
    isLoggingOut: boolean;
    openAuthModal: () => void;
    closeAuthModal: () => void;
    loginWithGoogle: () => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<Models.User<Models.Preferences> | null>(null);
    const [loading, setLoading] = useState(true);
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    useEffect(() => {
        checkUser();
    }, []);

    const checkUser = async () => {
        try {
            const currentUser = await account.get();
            setUser(currentUser);
        } catch (error) {
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const openAuthModal = () => setIsAuthModalOpen(true);
    const closeAuthModal = () => setIsAuthModalOpen(false);

    const loginWithGoogle = async () => {
        try {
            const origin = window.location.origin;
            await account.createOAuth2Session(
                OAuthProvider.Google,
                `${origin}/auth/callback`,
                origin
            );
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    const logout = async () => {
        setIsLoggingOut(true);
        try {
            // Artificial delay for smooth transition if needed, 
            // but usually a nice animation is better managed in the UI component
            await new Promise(resolve => setTimeout(resolve, 800));
            await account.deleteSession('current');
            setUser(null);
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setIsLoggingOut(false);
        }
    };

    return (
        <AuthContext.Provider value={{
            user,
            loading,
            isAuthModalOpen,
            isLoggingOut,
            openAuthModal,
            closeAuthModal,
            loginWithGoogle,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

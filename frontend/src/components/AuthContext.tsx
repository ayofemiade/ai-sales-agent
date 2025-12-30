'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { User } from '@supabase/supabase-js';

interface AuthContextType {
    user: User | null;
    userName: string | null;
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
    const [user, setUser] = useState<User | null>(null);
    const [userName, setUserName] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    useEffect(() => {
        const updateUserData = (user: User | null) => {
            setUser(user);
            setUserName(user?.user_metadata?.full_name || user?.user_metadata?.name || user?.email || null);
        };
        // Initial session check
        const getInitialSession = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            updateUserData(session?.user ?? null);
            setLoading(false);
        };

        getInitialSession();

        // Listen for auth state changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            updateUserData(session?.user ?? null);
            setLoading(false);
        });

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const openAuthModal = () => setIsAuthModalOpen(true);
    const closeAuthModal = () => setIsAuthModalOpen(false);

    const loginWithGoogle = async () => {
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}/auth/callback`,
                }
            });
            if (error) throw error;
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    const logout = async () => {
        setIsLoggingOut(true);
        try {
            await new Promise(resolve => setTimeout(resolve, 800));
            const { error } = await supabase.auth.signOut();
            if (error) throw error;
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
            userName,
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

# Milestone: UI/UX Overhaul - 48-Hour Sprint

**Project:** RecruitApp (formerly RecruitTalk)
**Timeline:** 48 hours
**Goal:** Create a stunning, modern,

 "sticky" user experience inspired by CSS Design Awards winners
**Deadline:** Before investors return from business trip

---

## Executive Summary

Transform RecruitApp from a functional MVP into a visually captivating, award-worthy web experience. The redesign will feature:

1. **Clean, white-first design** with navy + gold accents
2. **Sliding panel interface** - Ledger (left), Action Items (right), Profile (bottom)
3. **Top navigation bar** - All controls accessible from top
4. **Center-stage chat** - Agent conversation is the hero
5. **Dark mode toggle** - Inverted color scheme
6. **Monads.ch-inspired minimalism** - Sophisticated, restrained aesthetics
7. **Smooth animations** - Every interaction feels premium

---

## Design Philosophy

### Core Principles (Inspired by Monads.ch)

1. **Generous White Space** - Let elements breathe, don't cram
2. **Subtle Micro-Interactions** - Refined hover states, smooth transitions
3. **Typography Hierarchy** - Bold headlines, clean body text
4. **Modular Sections** - Each view tells one story
5. **Professional Minimalism** - Premium through simplicity
6. **Purpose-Driven Animation** - Motion guides attention, not just decoration

### RecruitApp-Specific Additions

- **Energy & Movement** - Sports = dynamism
- **Trust & Achievement** - Navy for trust, gold for success
- **Clarity & Guidance** - Students need clear CTAs
- **Accessibility** - High contrast, readable fonts, mobile-first

---

## Color System

### Light Mode (Primary)

```css
/* ===== LIGHT MODE (Default) ===== */

/* Base Colors */
--ra-bg-primary: #FFFFFF;              /* Pure white background */
--ra-bg-secondary: #F8F9FA;            /* Subtle gray for cards */
--ra-bg-elevated: #FFFFFF;             /* White with shadow for elevation */

/* Navy Accent */
--ra-navy: #0A2540;                    /* Deep professional navy */
--ra-navy-light: #1E3A5F;              /* Hover state */
--ra-navy-lighter: #E8EDF3;            /* Background tint */

/* Gold Accent */
--ra-gold: #C9A24A;                    /* Championship gold (muted, not garish) */
--ra-gold-light: #D4B15E;              /* Hover state */
--ra-gold-lighter: #F7F4ED;            /* Background tint */

/* Text */
--ra-text-primary: #1A1A1A;            /* Almost black */
--ra-text-secondary: #4A5568;          /* Gray for secondary content */
--ra-text-muted: #9CA3AF;              /* Lighter gray for hints */

/* Borders & Dividers */
--ra-border: #E5E7EB;                  /* Subtle gray borders */
--ra-border-focus: #C9A24A;            /* Gold focus state */

/* Shadows */
--ra-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--ra-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--ra-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--ra-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
```

### Dark Mode (Inverted)

```css
/* ===== DARK MODE (Toggle) ===== */

[data-theme="dark"] {
  /* Base Colors */
  --ra-bg-primary: #0A0E1A;            /* Deep dark blue-black */
  --ra-bg-secondary: #151B2E;          /* Slightly lighter for cards */
  --ra-bg-elevated: #1E2749;           /* Elevated surfaces */

  /* Navy becomes lighter in dark mode */
  --ra-navy: #5B7CA8;                  /* Lighter blue */
  --ra-navy-light: #7A98C4;            /* Even lighter on hover */
  --ra-navy-lighter: #1E2C42;          /* Background tint */

  /* Gold stays warm */
  --ra-gold: #E8C468;                  /* Brighter gold for dark bg */
  --ra-gold-light: #F0D17B;            /* Hover */
  --ra-gold-lighter: #2A2518;          /* Background tint */

  /* Text */
  --ra-text-primary: #F9FAFB;          /* Off-white */
  --ra-text-secondary: #D1D5DB;        /* Light gray */
  --ra-text-muted: #6B7280;            /* Muted gray */

  /* Borders */
  --ra-border: #2D3748;                /* Darker borders */
  --ra-border-focus: #E8C468;          /* Gold focus */

  /* Shadows */
  --ra-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --ra-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
  --ra-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  --ra-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6);
}
```

---

## Typography System

```css
/* ===== FONTS ===== */

/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* Font Families */
--ra-font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--ra-font-mono: 'JetBrains Mono', 'Fira Code', monospace; /* For code/data */

/* Font Sizes (Fluid Typography) */
--ra-text-xs: 0.75rem;                 /* 12px */
--ra-text-sm: 0.875rem;                /* 14px */
--ra-text-base: 1rem;                  /* 16px */
--ra-text-lg: 1.125rem;                /* 18px */
--ra-text-xl: 1.25rem;                 /* 20px */
--ra-text-2xl: 1.5rem;                 /* 24px */
--ra-text-3xl: 1.875rem;               /* 30px */
--ra-text-4xl: 2.25rem;                /* 36px */
--ra-text-5xl: clamp(2.5rem, 5vw, 3.5rem); /* 40px - 56px (fluid) */

/* Font Weights */
--ra-weight-normal: 400;
--ra-weight-medium: 500;
--ra-weight-semibold: 600;
--ra-weight-bold: 700;
--ra-weight-extrabold: 800;
--ra-weight-black: 900;

/* Line Heights */
--ra-leading-tight: 1.25;
--ra-leading-snug: 1.375;
--ra-leading-normal: 1.5;
--ra-leading-relaxed: 1.625;
--ra-leading-loose: 2;

/* Letter Spacing */
--ra-tracking-tight: -0.025em;
--ra-tracking-normal: 0;
--ra-tracking-wide: 0.025em;
```

---

## Spacing & Layout

```css
/* ===== SPACING SCALE ===== */

--ra-space-0: 0;
--ra-space-1: 0.25rem;    /* 4px */
--ra-space-2: 0.5rem;     /* 8px */
--ra-space-3: 0.75rem;    /* 12px */
--ra-space-4: 1rem;       /* 16px */
--ra-space-5: 1.25rem;    /* 20px */
--ra-space-6: 1.5rem;     /* 24px */
--ra-space-8: 2rem;       /* 32px */
--ra-space-10: 2.5rem;    /* 40px */
--ra-space-12: 3rem;      /* 48px */
--ra-space-16: 4rem;      /* 64px */
--ra-space-20: 5rem;      /* 80px */
--ra-space-24: 6rem;      /* 96px */

/* Border Radius */
--ra-radius-sm: 0.25rem;  /* 4px */
--ra-radius-md: 0.5rem;   /* 8px */
--ra-radius-lg: 0.75rem;  /* 12px */
--ra-radius-xl: 1rem;     /* 16px */
--ra-radius-full: 9999px; /* Pill shape */

/* Z-Index Layers */
--ra-z-base: 0;
--ra-z-dropdown: 1000;
--ra-z-sticky: 1020;
--ra-z-panel: 1030;       /* Sliding panels */
--ra-z-modal: 1040;
--ra-z-popover: 1050;
--ra-z-tooltip: 1060;
```

---

## Animation System

```css
/* ===== TRANSITIONS & ANIMATIONS ===== */

/* Duration */
--ra-duration-fast: 150ms;
--ra-duration-base: 250ms;
--ra-duration-slow: 350ms;
--ra-duration-slower: 500ms;

/* Easing (Custom Cubic Bezier) */
--ra-ease-in: cubic-bezier(0.4, 0, 1, 1);
--ra-ease-out: cubic-bezier(0, 0, 0.2, 1);
--ra-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ra-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Bouncy */

/* Common Transitions */
--ra-transition-all: all var(--ra-duration-base) var(--ra-ease-in-out);
--ra-transition-colors: background-color var(--ra-duration-base) var(--ra-ease-in-out),
                        color var(--ra-duration-base) var(--ra-ease-in-out),
                        border-color var(--ra-duration-base) var(--ra-ease-in-out);
--ra-transition-transform: transform var(--ra-duration-base) var(--ra-ease-spring);
```

---

## Layout Architecture

### New Page Structure

```
┌─────────────────────────────────────────────────────────────┐
│  TOP NAV BAR (Fixed, always visible)                        │
│  ┌────────┬──────────────────────────────────┬──────────┐  │
│  │ Logo   │  Profile • Ledger • Actions      │ 🌙 Dark │  │
│  └────────┴──────────────────────────────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│                 CHAT INTERFACE (Center Stage)                │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Session Selector (Dropdown at top)                   │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │                                                        │  │
│  │  [User Message]                                        │  │
│  │                                        [Agent Message] │  │
│  │  [User Message]                                        │  │
│  │                                        [Agent Message] │  │
│  │                                                        │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  Message Input Box                          [Send →]  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘

SLIDING PANELS (Overlay on demand):

LEDGER (Slides from left):
┌─────────────────────────┐
│ 📖 My Ledger            │
│ ─────────────────────── │
│ Entry 1...              │
│ Entry 2...              │
│ [+ Add Entry]           │
└─────────────────────────┘

ACTION ITEMS (Slides from right):
                    ┌─────────────────────────┐
                    │ ✅ Action Items         │
                    │ ─────────────────────── │
                    │ ☐ Task 1                │
                    │ ☑ Task 2 (Done)         │
                    │ [+ New Action]          │
                    └─────────────────────────┘

PROFILE (Slides from bottom):
┌─────────────────────────────────────────────────────────────┐
│  👤 Your Profile                                     [Close]│
│  ─────────────────────────────────────────────────────────  │
│  Name: [John Doe]         Sport: [Basketball]              │
│  Grade: [Junior]          Position: [Forward]              │
│  ─────────────────────────────────────────────────────────  │
│  [Save Changes]                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Top Navigation Bar

**Purpose:** Persistent access to key features without sidebar clutter

**Structure:**
```html
<nav class="ra-topnav">
  <div class="ra-topnav-left">
    <a href="/" class="ra-logo">
      <span class="ra-logo-icon">🎯</span>
      <span class="ra-logo-text">RecruitApp</span>
    </a>
  </div>

  <div class="ra-topnav-center">
    <button class="ra-nav-btn" data-panel="ledger">
      <span class="ra-nav-icon">📖</span>
      <span class="ra-nav-label">Ledger</span>
    </button>
    <button class="ra-nav-btn" data-panel="actions">
      <span class="ra-nav-icon">✅</span>
      <span class="ra-nav-label">Action Items</span>
    </button>
    <button class="ra-nav-btn" data-panel="profile">
      <span class="ra-nav-icon">👤</span>
      <span class="ra-nav-label">Profile</span>
    </button>
  </div>

  <div class="ra-topnav-right">
    <button class="ra-theme-toggle" aria-label="Toggle dark mode">
      <span class="ra-theme-icon light-icon">☀️</span>
      <span class="ra-theme-icon dark-icon">🌙</span>
    </button>
    <div class="ra-user-menu">
      <img src="avatar.jpg" alt="User" class="ra-avatar" />
      <span class="ra-username">John</span>
    </div>
  </div>
</nav>
```

**Styling:**
```css
.ra-topnav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--ra-bg-primary);
  border-bottom: 1px solid var(--ra-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--ra-space-6);
  z-index: var(--ra-z-sticky);
  box-shadow: var(--ra-shadow-sm);
  transition: var(--ra-transition-colors);
}

.ra-logo {
  display: flex;
  align-items: center;
  gap: var(--ra-space-2);
  font-weight: var(--ra-weight-bold);
  font-size: var(--ra-text-xl);
  color: var(--ra-navy);
  text-decoration: none;
  transition: var(--ra-transition-transform);
}

.ra-logo:hover {
  transform: translateY(-2px);
}

.ra-nav-btn {
  display: flex;
  align-items: center;
  gap: var(--ra-space-2);
  padding: var(--ra-space-2) var(--ra-space-4);
  background: transparent;
  border: none;
  border-radius: var(--ra-radius-md);
  font-size: var(--ra-text-sm);
  font-weight: var(--ra-weight-medium);
  color: var(--ra-text-secondary);
  cursor: pointer;
  transition: var(--ra-transition-all);
}

.ra-nav-btn:hover {
  background: var(--ra-gold-lighter);
  color: var(--ra-navy);
  transform: translateY(-1px);
}

.ra-nav-btn.active {
  background: var(--ra-gold);
  color: white;
  box-shadow: var(--ra-shadow-md);
}
```

**Behavior:**
- Clicking Ledger/Actions/Profile opens sliding panel
- Active state shows which panel is open
- Smooth hover transitions
- Mobile: Collapse to hamburger menu

---

### 2. Sliding Panels System

**Technical Implementation:**

Each panel is a fixed-position overlay that slides in from its designated direction:

```css
/* Base Panel Structure */
.ra-panel {
  position: fixed;
  background: var(--ra-bg-primary);
  box-shadow: var(--ra-shadow-xl);
  z-index: var(--ra-z-panel);
  overflow-y: auto;
  transition: transform var(--ra-duration-slow) var(--ra-ease-out);
}

/* Ledger Panel (Left) */
.ra-panel-ledger {
  top: 64px; /* Below nav */
  left: 0;
  bottom: 0;
  width: 400px;
  max-width: 90vw;
  transform: translateX(-100%); /* Hidden by default */
  border-right: 1px solid var(--ra-border);
}

.ra-panel-ledger.open {
  transform: translateX(0); /* Slide in */
}

/* Action Items Panel (Right) */
.ra-panel-actions {
  top: 64px;
  right: 0;
  bottom: 0;
  width: 400px;
  max-width: 90vw;
  transform: translateX(100%);
  border-left: 1px solid var(--ra-border);
}

.ra-panel-actions.open {
  transform: translateX(0);
}

/* Profile Panel (Bottom) */
.ra-panel-profile {
  left: 0;
  right: 0;
  bottom: 0;
  height: 60vh;
  max-height: 600px;
  transform: translateY(100%);
  border-top: 1px solid var(--ra-border);
}

.ra-panel-profile.open {
  transform: translateY(0);
}

/* Backdrop (when panel is open) */
.ra-panel-backdrop {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: calc(var(--ra-z-panel) - 1);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--ra-duration-base) var(--ra-ease-out);
}

.ra-panel-backdrop.visible {
  opacity: 1;
  pointer-events: auto;
}
```

**JavaScript Control:**
```javascript
// Panel state management
const panels = {
  ledger: false,
  actions: false,
  profile: false
};

function togglePanel(panelName) {
  // Close all other panels
  Object.keys(panels).forEach(key => {
    if (key !== panelName && panels[key]) {
      closePanel(key);
    }
  });

  // Toggle target panel
  panels[panelName] = !panels[panelName];
  const panel = document.querySelector(`.ra-panel-${panelName}`);
  const backdrop = document.querySelector('.ra-panel-backdrop');
  const btn = document.querySelector(`[data-panel="${panelName}"]`);

  if (panels[panelName]) {
    panel.classList.add('open');
    backdrop.classList.add('visible');
    btn.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent scroll
  } else {
    closePanel(panelName);
  }
}

function closePanel(panelName) {
  panels[panelName] = false;
  const panel = document.querySelector(`.ra-panel-${panelName}`);
  const backdrop = document.querySelector('.ra-panel-backdrop');
  const btn = document.querySelector(`[data-panel="${panelName}"]`);

  panel.classList.remove('open');
  backdrop.classList.remove('visible');
  btn.classList.remove('active');

  // Only restore scroll if all panels are closed
  const anyOpen = Object.values(panels).some(isOpen => isOpen);
  if (!anyOpen) {
    document.body.style.overflow = '';
  }
}

// Close on backdrop click
document.querySelector('.ra-panel-backdrop').addEventListener('click', () => {
  Object.keys(panels).forEach(closePanel);
});

// Close on ESC key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    Object.keys(panels).forEach(closePanel);
  }
});
```

---

### 3. Chat Interface (Center Stage)

**Purpose:** The primary interaction point - should feel clean, spacious, and inviting

**Structure:**
```html
<main class="ra-chat-container">
  <!-- Session Selector -->
  <div class="ra-chat-header">
    <select class="ra-session-selector">
      <option value="new">➕ New Conversation</option>
      <option value="1">Profile Setup - March 15</option>
      <option value="2">NCAA Eligibility - March 14</option>
    </select>
  </div>

  <!-- Messages -->
  <div class="ra-chat-messages">
    <div class="ra-message ra-message-user">
      <div class="ra-message-bubble">
        How do I contact college coaches?
      </div>
      <div class="ra-message-meta">2:34 PM</div>
    </div>

    <div class="ra-message ra-message-agent">
      <div class="ra-message-avatar">
        <img src="coach-alex.png" alt="Coach Alex" />
      </div>
      <div class="ra-message-content">
        <div class="ra-message-name">Coach Alex</div>
        <div class="ra-message-bubble">
          Great question! Here's a step-by-step approach...
        </div>
        <div class="ra-message-meta">2:34 PM</div>
      </div>
    </div>

    <!-- Typing Indicator -->
    <div class="ra-typing-indicator">
      <div class="ra-typing-avatar">
        <img src="coach-alex.png" alt="Coach Alex" />
      </div>
      <div class="ra-typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
  </div>

  <!-- Input Box -->
  <div class="ra-chat-input">
    <textarea
      class="ra-input-field"
      placeholder="Ask Coach Alex anything..."
      rows="1"
    ></textarea>
    <button class="ra-send-btn">
      <span class="ra-send-icon">→</span>
    </button>
  </div>
</main>
```

**Styling:**
```css
.ra-chat-container {
  margin-top: 64px; /* Below fixed nav */
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 var(--ra-space-6);
}

/* Session Selector */
.ra-session-selector {
  width: 100%;
  padding: var(--ra-space-3) var(--ra-space-4);
  font-size: var(--ra-text-base);
  font-weight: var(--ra-weight-medium);
  color: var(--ra-text-primary);
  background: var(--ra-bg-secondary);
  border: 1px solid var(--ra-border);
  border-radius: var(--ra-radius-lg);
  cursor: pointer;
  transition: var(--ra-transition-all);
  margin-bottom: var(--ra-space-4);
}

.ra-session-selector:hover {
  border-color: var(--ra-gold);
  box-shadow: var(--ra-shadow-sm);
}

/* Messages Container */
.ra-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--ra-space-4) 0;
  display: flex;
  flex-direction: column;
  gap: var(--ra-space-4);
}

/* Message Bubbles */
.ra-message {
  display: flex;
  gap: var(--ra-space-3);
  animation: messageSlideIn 0.3s var(--ra-ease-spring);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ra-message-user {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.ra-message-bubble {
  padding: var(--ra-space-3) var(--ra-space-4);
  border-radius: var(--ra-radius-lg);
  max-width: 70%;
  line-height: var(--ra-leading-relaxed);
}

.ra-message-user .ra-message-bubble {
  background: var(--ra-navy);
  color: white;
  border-bottom-right-radius: var(--ra-radius-sm);
}

.ra-message-agent .ra-message-bubble {
  background: var(--ra-bg-secondary);
  color: var(--ra-text-primary);
  border: 1px solid var(--ra-border);
  border-bottom-left-radius: var(--ra-radius-sm);
}

/* Typing Indicator */
.ra-typing-dots {
  display: flex;
  gap: 4px;
  padding: var(--ra-space-3) var(--ra-space-4);
  background: var(--ra-bg-secondary);
  border-radius: var(--ra-radius-lg);
  border-bottom-left-radius: var(--ra-radius-sm);
}

.ra-typing-dots span {
  width: 8px;
  height: 8px;
  background: var(--ra-gold);
  border-radius: 50%;
  animation: typingDot 1.4s infinite;
}

.ra-typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.ra-typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingDot {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* Input Box */
.ra-chat-input {
  display: flex;
  gap: var(--ra-space-3);
  padding: var(--ra-space-4) 0;
  border-top: 1px solid var(--ra-border);
  background: var(--ra-bg-primary);
}

.ra-input-field {
  flex: 1;
  padding: var(--ra-space-3) var(--ra-space-4);
  font-size: var(--ra-text-base);
  font-family: var(--ra-font-primary);
  color: var(--ra-text-primary);
  background: var(--ra-bg-secondary);
  border: 1px solid var(--ra-border);
  border-radius: var(--ra-radius-lg);
  resize: none;
  max-height: 150px;
  transition: var(--ra-transition-all);
}

.ra-input-field:focus {
  outline: none;
  border-color: var(--ra-gold);
  box-shadow: 0 0 0 3px var(--ra-gold-lighter);
}

.ra-send-btn {
  width: 48px;
  height: 48px;
  background: var(--ra-gold);
  border: none;
  border-radius: var(--ra-radius-lg);
  color: white;
  font-size: var(--ra-text-xl);
  font-weight: var(--ra-weight-bold);
  cursor: pointer;
  transition: var(--ra-transition-transform);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ra-send-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: var(--ra-shadow-md);
}

.ra-send-btn:active {
  transform: translateY(0) scale(0.95);
}
```

---

### 4. Dark Mode Toggle

**Implementation:**
```javascript
// Theme toggle functionality
const themeToggle = document.querySelector('.ra-theme-toggle');
const root = document.documentElement;

// Check for saved preference or default to light
const currentTheme = localStorage.getItem('theme') || 'light';
root.setAttribute('data-theme', currentTheme);

themeToggle.addEventListener('click', () => {
  const current = root.getAttribute('data-theme');
  const next = current === 'light' ? 'dark' : 'light';

  root.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);

  // Animate the toggle button
  themeToggle.style.transform = 'rotate(360deg)';
  setTimeout(() => {
    themeToggle.style.transform = '';
  }, 500);
});
```

**Styling:**
```css
.ra-theme-toggle {
  width: 40px;
  height: 40px;
  border: none;
  background: var(--ra-bg-secondary);
  border-radius: var(--ra-radius-full);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--ra-transition-transform), background-color 0.3s;
}

.ra-theme-toggle:hover {
  background: var(--ra-gold-lighter);
  transform: scale(1.1);
}

.ra-theme-icon {
  font-size: 20px;
  transition: opacity 0.3s;
}

/* Show/hide based on theme */
[data-theme="light"] .dark-icon,
[data-theme="dark"] .light-icon {
  display: none;
}
```

---

## Landing Page Redesign

### Hero Section

```html
<section class="ra-hero">
  <div class="ra-hero-content">
    <h1 class="ra-hero-title">
      Turn Recruiting Confusion<br/>
      Into <span class="ra-highlight">Championship Clarity</span>
    </h1>
    <p class="ra-hero-subtitle">
      AI-powered guidance for high school athletes navigating the college recruiting process
    </p>
    <div class="ra-hero-cta">
      <a href="/signup" class="ra-btn ra-btn-primary">
        Start Your Journey →
      </a>
      <a href="#features" class="ra-btn ra-btn-secondary">
        Learn More
      </a>
    </div>
  </div>

  <div class="ra-hero-visual">
    <!-- Animated illustration or screenshot -->
  </div>
</section>
```

**Styling:**
```css
.ra-hero {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: var(--ra-space-12);
  padding: var(--ra-space-20) var(--ra-space-6);
  background: linear-gradient(135deg, var(--ra-bg-primary) 0%, var(--ra-gold-lighter) 100%);
}

.ra-hero-title {
  font-size: var(--ra-text-5xl);
  font-weight: var(--ra-weight-black);
  line-height: var(--ra-leading-tight);
  color: var(--ra-navy);
  margin-bottom: var(--ra-space-6);
  letter-spacing: var(--ra-tracking-tight);
}

.ra-highlight {
  color: var(--ra-gold);
  position: relative;
}

.ra-highlight::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: right;
  animation: underline 1s forwards 0.5s;
}

@keyframes underline {
  to {
    transform: scaleX(1);
    transform-origin: left;
  }
}

.ra-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--ra-space-2);
  padding: var(--ra-space-4) var(--ra-space-6);
  font-size: var(--ra-text-base);
  font-weight: var(--ra-weight-semibold);
  text-decoration: none;
  border-radius: var(--ra-radius-lg);
  transition: var(--ra-transition-transform);
}

.ra-btn-primary {
  background: var(--ra-navy);
  color: white;
  box-shadow: var(--ra-shadow-md);
}

.ra-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--ra-shadow-lg);
}

.ra-btn-secondary {
  background: transparent;
  color: var(--ra-navy);
  border: 2px solid var(--ra-navy);
}

.ra-btn-secondary:hover {
  background: var(--ra-navy-lighter);
}
```

---

## Implementation Timeline

### Day 1 (12-14 hours)

#### Morning (4-5 hours)
- [ ] **Setup design system CSS**
  - Create `redesign.css` with all color/spacing/typography variables
  - Import Inter font
  - Setup theme toggle infrastructure

#### Afternoon (4-5 hours)
- [ ] **Build top navigation**
  - HTML structure
  - CSS styling (light + dark mode)
  - JavaScript panel controls

#### Evening (3-4 hours)
- [ ] **Implement sliding panels**
  - Panel HTML structure (Ledger, Actions, Profile)
  - Slide-in animations
  - Backdrop + close logic
  - Test all panel interactions

### Day 2 (12-14 hours)

#### Morning (5-6 hours)
- [ ] **Redesign chat interface**
  - New message bubble styling
  - Typing indicator animation
  - Session selector
  - Input box with auto-resize

#### Afternoon (4-5 hours)
- [ ] **Landing page overhaul**
  - Hero section with gradient
  - Feature cards
  - CTA buttons with hover states

#### Evening (3-4 hours)
- [ ] **Polish & responsive**
  - Mobile layouts (hamburger menu, stacked panels)
  - Tablet breakpoints
  - Cross-browser testing
  - Performance optimization (lazy-load animations)

---

## Technical Notes

### CSS Organization

```
recruiting/static/recruiting/css/
├── redesign.css           (New design system - import first)
├── recruiting.css         (Legacy - gradually migrate)
└── components/
    ├── topnav.css
    ├── panels.css
    ├── chat.css
    └── buttons.css
```

### JavaScript Organization

```javascript
// redesign.js

// Theme toggle
import { initThemeToggle } from './theme.js';

// Panel system
import { PanelController } from './panels.js';

// Chat enhancements
import { ChatUI } from './chat.js';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  const panels = new PanelController();
  const chat = new ChatUI();
});
```

### Performance Considerations

1. **CSS Variables** - Browser-native, no JS overhead
2. **Lazy Animations** - Only animate elements in viewport
3. **Debounced Resize** - Prevent layout thrashing on window resize
4. **Prefers-Reduced-Motion** - Respect accessibility preferences

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Success Metrics

### Visual Impact (What Investors See)
- ✅ Clean, modern, professional first impression
- ✅ Smooth animations that don't feel gimmicky
- ✅ Clear information hierarchy
- ✅ "This team understands design" reaction

### Technical Quality
- ✅ 60 FPS animations on all interactions
- ✅ Lighthouse score: 90+ Performance, 100 Accessibility
- ✅ Works flawlessly on Chrome, Safari, Firefox
- ✅ Mobile-responsive (iPhone, iPad, Android)

### User Experience
- ✅ Intuitive navigation (no explanation needed)
- ✅ Fast perceived performance (instant feedback)
- ✅ Accessible (keyboard nav, screen readers, WCAG AA)
- ✅ "Sticky" - want to keep exploring

---

## Risks & Mitigation

**Risk:** Panels feel janky on slower devices
**Mitigation:** Use CSS transforms (GPU-accelerated), test on mid-range devices

**Risk:** Too much white space feels empty
**Mitigation:** Add subtle background patterns, gradient accents

**Risk:** Dark mode looks washed out
**Mitigation:** Boost contrast, test with actual dark mode users

**Risk:** 48 hours not enough time
**Mitigation:** Prioritize core pages (landing, agent chat), defer edge cases

---

## Approved Design Plan?

**Once you approve this plan, I'll:**

1. Create the CSS design system file
2. Build the top navigation
3. Implement sliding panels
4. Redesign chat interface
5. Overhaul landing page
6. Add dark mode toggle
7. Polish and test

**Ready to proceed? Any changes to the plan before I start building?**

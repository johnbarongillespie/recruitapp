/* ============================================================================
   RECRUITAPP - UI REDESIGN JAVASCRIPT
   Handles: Theme toggle, sliding panels, smooth interactions
   ============================================================================ */

(function() {
  'use strict';

  // ============================================================================
  // 1. THEME TOGGLE (Dark Mode)
  // ============================================================================

  function initThemeToggle() {
    const themeToggle = document.querySelector('.ra-theme-toggle');
    if (!themeToggle) return;

    const root = document.documentElement;

    // Check for saved preference or default to light
    const currentTheme = localStorage.getItem('ra-theme') || 'light';
    root.setAttribute('data-theme', currentTheme);

    themeToggle.addEventListener('click', () => {
      const current = root.getAttribute('data-theme');
      const next = current === 'light' ? 'dark' : 'light';

      root.setAttribute('data-theme', next);
      localStorage.setItem('ra-theme', next);

      // Animate the toggle button
      themeToggle.style.transform = 'rotate(360deg)';
      setTimeout(() => {
        themeToggle.style.transform = '';
      }, 500);

      console.log(`Theme switched to: ${next}`);
    });
  }

  // ============================================================================
  // 2. SLIDING PANELS CONTROLLER
  // ============================================================================

  function initPanels() {
    // Panel state
    const panels = {
      ledger: false,
      actions: false,
      profile: false
    };

    // Get elements
    const backdrop = document.querySelector('.ra-panel-backdrop');

    // Panel buttons
    const panelButtons = document.querySelectorAll('[data-panel]');

    // Close buttons
    const closeButtons = document.querySelectorAll('.ra-panel-close');

    // Toggle panel function
    function togglePanel(panelName) {
      console.log(`Toggling panel: ${panelName}`);

      // Close all other panels
      Object.keys(panels).forEach(key => {
        if (key !== panelName && panels[key]) {
          closePanel(key);
        }
      });

      // Toggle target panel
      panels[panelName] = !panels[panelName];
      const panel = document.querySelector(`.ra-panel-${panelName}`);
      const btn = document.querySelector(`[data-panel="${panelName}"]`);

      if (!panel) {
        console.error(`Panel not found: ra-panel-${panelName}`);
        return;
      }

      if (panels[panelName]) {
        // Open
        panel.classList.add('open');
        if (backdrop) backdrop.classList.add('visible');
        if (btn) btn.classList.add('active');
        document.body.style.overflow = 'hidden';
      } else {
        // Close
        closePanel(panelName);
      }
    }

    // Close panel function
    function closePanel(panelName) {
      panels[panelName] = false;
      const panel = document.querySelector(`.ra-panel-${panelName}`);
      const btn = document.querySelector(`[data-panel="${panelName}"]`);

      if (panel) panel.classList.remove('open');
      if (btn) btn.classList.remove('active');

      // Only restore scroll if all panels are closed
      const anyOpen = Object.values(panels).some(isOpen => isOpen);
      if (!anyOpen) {
        if (backdrop) backdrop.classList.remove('visible');
        document.body.style.overflow = '';
      }
    }

    // Close all panels
    function closeAllPanels() {
      Object.keys(panels).forEach(closePanel);
    }

    // Attach button listeners
    panelButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const panelName = btn.getAttribute('data-panel');
        togglePanel(panelName);
      });
    });

    // Close buttons
    closeButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const panel = e.target.closest('.ra-panel');
        if (panel) {
          const panelName = panel.className.match(/ra-panel-(\w+)/)[1];
          closePanel(panelName);
        }
      });
    });

    // Backdrop click closes all
    if (backdrop) {
      backdrop.addEventListener('click', closeAllPanels);
    }

    // ESC key closes all
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeAllPanels();
      }
    });

    console.log('Panel system initialized');
  }

  // ============================================================================
  // 3. CHAT INTERFACE ENHANCEMENTS
  // ============================================================================

  function initChatEnhancements() {
    const chatInput = document.querySelector('.ra-input-field');
    const sendBtn = document.querySelector('.ra-send-btn');
    const messagesContainer = document.querySelector('.ra-chat-messages');

    if (!chatInput || !sendBtn) return;

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = chatInput.scrollHeight + 'px';
    });

    // Send on Enter (Shift+Enter for newline)
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
      }
    });

    // Auto-scroll to bottom when new messages appear
    if (messagesContainer) {
      const observer = new MutationObserver(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      });

      observer.observe(messagesContainer, {
        childList: true,
        subtree: true
      });
    }

    console.log('Chat enhancements initialized');
  }

  // ============================================================================
  // 4. SMOOTH SCROLL FOR ANCHORS
  // ============================================================================

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;

        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  // ============================================================================
  // 5. INITIALIZE ON DOM READY
  // ============================================================================

  function init() {
    console.log('RecruitApp UI initialized');
    initThemeToggle();
    initPanels();
    initChatEnhancements();
    initSmoothScroll();
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

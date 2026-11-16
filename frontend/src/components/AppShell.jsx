import React, { useState } from 'react';
import Sidebar from './Sidebar';

/**
 * AppShell — Main responsive layout shell supporting Liquid Glass aesthetics.
 */
export default function AppShell({ children }) {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-midnight-950 text-frost-100 ambient-mesh">
      {/* Desktop / Mobile Sidebar */}
      <Sidebar
        isOpen={isMobileNavOpen}
        onClose={() => setIsMobileNavOpen(false)}
      />

      {/* Main Content Viewport */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Pass mobile toggle handler down to children or wrapper */}
        <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col">
          {React.cloneElement(children, {
            onToggleMobileNav: () => setIsMobileNavOpen(!isMobileNavOpen)
          })}
        </div>
      </div>
    </div>
  );
}

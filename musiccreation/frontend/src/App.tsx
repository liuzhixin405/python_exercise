import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import Introduction from './components/Introduction';
import News from './components/News';

function App() {
  const [currentSection, setCurrentSection] = useState('introduction');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState<string | null>(null);
  const [scrollProgress, setScrollProgress] = useState(0);
  const mainRef = useRef<HTMLDivElement>(null);

  const handleSectionChange = (section: string) => {
    setCurrentSection(section);
    const element = document.getElementById(section);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleLogin = (username: string) => {
    setIsLoggedIn(true);
    setCurrentUser(username);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
  };

  // 监听滚动事件
  useEffect(() => {
    const handleScroll = () => {
      if (!mainRef.current) return;
      
      const scrollTop = window.pageYOffset;
      const docHeight = document.body.offsetHeight - window.innerHeight;
      const scrollPercent = (scrollTop / docHeight) * 100;
      setScrollProgress(scrollPercent);

      // 根据滚动位置确定当前section
      const sections = ['introduction', 'news'];
      const sectionElements = sections.map(id => document.getElementById(id));
      
      for (let i = sectionElements.length - 1; i >= 0; i--) {
        const element = sectionElements[i];
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= window.innerHeight * 0.5) {
            setCurrentSection(sections[i]);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 监听URL变化
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (hash && ['introduction', 'news'].includes(hash)) {
      setCurrentSection(hash);
    }
  }, []);

  // 更新URL
  useEffect(() => {
    window.location.hash = currentSection;
  }, [currentSection]);

  return (
    <div className="App" ref={mainRef}>
      <Navbar 
        currentSection={currentSection} 
        onSectionChange={handleSectionChange}
        onAdminClick={() => {}} // 空函数，因为现在直接跳转
        scrollProgress={scrollProgress}
        isLoggedIn={isLoggedIn}
        currentUser={currentUser}
        onLogin={handleLogin}
        onLogout={handleLogout}
      />
      
      <main>
        <section id="introduction">
          <Introduction />
        </section>
        
        <section id="news">
          <News isLoggedIn={isLoggedIn} currentUser={currentUser} />
        </section>
      </main>
    </div>
  );
}

export default App;

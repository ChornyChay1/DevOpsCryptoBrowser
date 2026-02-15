// src/components/Header.jsx
import React from 'react';

function Header({ currentPrice }) {
  return (
      <header className="header">
        <div className="logo">CryptoExplorer</div>
        <div className="price">
          BTC/USD <span>${currentPrice ? currentPrice.toFixed(2) : '—'}</span>
        </div>
      </header>
  );
}

export default Header;
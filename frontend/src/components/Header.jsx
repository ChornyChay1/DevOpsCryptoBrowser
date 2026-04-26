// src/components/Header.jsx
import React from 'react';
import logo_img from '../img/logo.svg'
function Header({ currentPrice }) {
  return (
      <header className="header">
        <div className="logo">
            <img src={logo_img} alt="logo" className="logo_img" />
            CryptoExplorer 666
        </div>
        <div className="price">
          BTC/USD <span>${currentPrice ? currentPrice.toFixed(2) : '—'}</span>
        </div>
      </header>
  );
}

export default Header;
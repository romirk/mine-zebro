import effects from "./NavBar.module.css";
import logo from "./lunarZebro.png";
import battery from "./battery.png";


function NavBar() {
  return (
    <div>
      <nav className={effects.navBar}>
        <img src = {logo} alt = 'logo' className = {effects.logo}/>
        <h1 className={effects.title}>LZ Mine Rover</h1>
        <ul className={effects.stats}>
          <li className = {effects.stats1}>Stats1</li>
          <li className = {effects.stats2}>Stats2</li>
          <li className = {effects.stats3}>Stats3</li>
          <li className = {effects.stats4}>Stats4</li>
        </ul>
        <img src = {battery} alt = 'battery' className = {effects.battery}/>
      </nav>
    </div>
  );
}

export default NavBar;

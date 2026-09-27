import storePhoto from "../assets/campuscustomss_store.webp";
import "./AboutPage.css";

export default function AboutPage() {
  return (
    <div className="about">
      <h1 className="page-title">About Campus Customs</h1>
      <p className="page-subtitle">
        A New Haven shop run on school spirit, honest stock counts, and a soft spot for
        good merch.
      </p>

      <div className="about__split">
        <div className="about__media">
          <img src={storePhoto} alt="The Campus Customs storefront" />
        </div>
        <div className="about__body">
          <p>
            Campus Customs started as a simple idea: Yale gear should feel personal, not
            mass-produced. We work with a small set of local printers and suppliers so every
            hoodie, tee, and crewneck actually holds up to campus winters, tailgates, and
            everything in between.
          </p>
          <p>
            Our racks cover every corner of Bulldog life — residential colleges, club sports,
            grad school pride, and the classics that never go out of style. Whether you're a
            first-year finding your college's colors for the first time, a parent stocking up
            before Family Weekend, or an alum who still knows every fight song, there's
            something here with your name on it.
          </p>
          <p>
            We keep our online shop honest: what you see in stock is what's actually on the
            shelf, and our chat assistant is there to help you track down a size, a color, or
            the perfect gift without the guesswork.
          </p>
        </div>
      </div>
    </div>
  );
}

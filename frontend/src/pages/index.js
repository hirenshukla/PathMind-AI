export async function getServerSideProps() {
  return {
    redirect: {
      destination: "/app.html",
      permanent: false,
    },
  };
}

export default function Home() {
  return null;
}

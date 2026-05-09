import { useState, useEffect, useRef } from "react";

/** Debounce a value by delay ms */
export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

/** Fetch data on mount or when deps change */
export function useFetch(fetchFn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;
    setLoading(true);
    setError(null);
    fetchFn()
      .then((result) => {
        if (isMounted.current) setData(result);
      })
      .catch((err) => {
        if (isMounted.current) setError(err.message || "An error occurred");
      })
      .finally(() => {
        if (isMounted.current) setLoading(false);
      });
    return () => { isMounted.current = false; };
  }, deps);

  return { data, loading, error };
}

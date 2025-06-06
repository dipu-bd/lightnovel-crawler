import type { SupportedSource } from '@/types';
import { stringifyError } from '@/utils/errors';
import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';

export function useSupportedSources() {
  const [refreshId, setRefreshId] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [data, setData] = useState<SupportedSource[]>([]);

  const fetchSupportedSources = async () => {
    try {
      setError(undefined);
      const res = await axios.get<SupportedSource[]>(
        '/api/meta/supported-sources'
      );
      setData(res.data);
    } catch (err) {
      setError(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSupportedSources();
  }, [refreshId]);

  const refresh = useCallback(() => {
    setRefreshId((v) => v + 1);
  }, []);

  return { data, loading, error, refresh };
}

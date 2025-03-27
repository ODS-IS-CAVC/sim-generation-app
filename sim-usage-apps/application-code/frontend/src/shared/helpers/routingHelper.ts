import router from '@/router';
import { useRoutingStore } from '@/stores/routing/routing';

/**
 * ユーザーがログイン前にアクセスしようとしたページにリダイレクトします。
 * @returns {void}
 */
export function redirectToRequestRoute(): void {
  const routingStore = useRoutingStore();

  if (!routingStore.redirectFrom) {
    router.push('/search');
    return;
  }

  if (routingStore.redirectFrom === 'scenario') {
    router.push({
      name: routingStore.redirectFrom,

      query: {
        uuid: routingStore.uuid,
      },
    });
  } else {
    router.push({
      name: routingStore.redirectFrom,
    });
  }

  routingStore.setRedirectFrom(null);
  routingStore.setUuid(null);
}

import type { Router, RouteRecordName } from 'vue-router';
import { useRoutingStore } from '@/stores/routing/routing';
import {
  catalogConsoleLog,
  errorToString,
  ConsoleLogLevel,
} from '@/shared/helpers/consoleLogHelper';

export const authenticationGuard = (router: Router) => {
  router.beforeEach(async (to, from) => {
    try {
      const routingStore = useRoutingStore();

      //UUID値の取得
      const uuidKey = 'uuid';
      const uuidValue = to.query[uuidKey];
      if (uuidValue !== undefined) {
        routingStore.setUuid(uuidValue);
      }

      const path = to.path;
      // ログイン要な画面の遷移  「/」は5050の場合に対応
      if (!router.hasRoute(to.name) && path !== '/') {
        return { name: 'error/not-found' };
      }

      // 子システムのルートパスなら(routeがundefinedの場合)、ログイン済みの場合にsearch画面へ遷移
      const gotoHomePaths: (RouteRecordName | null | undefined)[] = [undefined];
      // 実装例: 注文画面への直接アクセスを禁止してカタログ画面から入り直させる
      // const orderingPaths: (RouteRecordName | null | undefined)[] = [
      //   'ordering/checkout',
      //   'ordering/done',
      // ];
      // if (orderingPaths.includes(to.name) && !from.name) {
      //   return { name: 'catalog' };
      // }

      // 子システムのルートパスの場合、ログイン済みなのでHome画面へ遷移する。
      if (gotoHomePaths.includes(to.name)) {
        routingStore.setRedirectFrom(null);
        return { name: 'search' };
      } else {
        return true; //trueの場合は、target画面に遷移する
      }
    } catch (error) {
      catalogConsoleLog(
        ConsoleLogLevel.ERROR,
        'authenticationGuard router 異常:' +
          errorToString(error) +
          ' from:' +
          from.name,
        'authenticationGuard.ts',
        'router.beforeEach',
        true,
        'authenticationGuard router 異常:' +
          errorToString(error) +
          ' from:' +
          from.name,
      );
      return { name: 'error/not-found' };
    }
  });
};

import { defineStore } from 'pinia';

export const useMessageStore = defineStore({
  id: 'message',
  state: () => ({
    _id: '',
    _messageParm1: '',
    _messageParm2: '',
    _messageParm3: '',
    _type: '',
  }),
  actions: {
    /**
     * メッセージIDからメッセージと種別を取得する。
     * @param messageParm メッセージIDとパラメータ
     * @param type メッセージ種別
     */
    async getMessageByMessageId(messageParm: Array, type: string) {
      if (messageParm) {
        this._id = messageParm[0];
        if (messageParm.length === 4) {
          this._messageParm1 = messageParm[1];
          this._messageParm2 = messageParm[2];
          this._messageParm3 = messageParm[3];
        } else if (messageParm.length === 3) {
          this._messageParm1 = messageParm[1];
          this._messageParm2 = messageParm[2];
        } else if (messageParm.length === 2) {
          this._messageParm1 = messageParm[1];
        }
        this._type = type;
      }
    },
    /**
     * メッセージIDを設定する。
     * @param messageId メッセージID
     */
    setMessageId(messageId: string) {
      this._id = messageId;
    },
    /**
     * メッセージ種別を設定する。
     * @param messageType メッセージ種別
     */
    setMessageType(messageType: string) {
      this._type = messageType;
    },
  },
  getters: {
    /**
     * メッセージIDを取得する。
     */
    getMessageId(state) {
      return state._id;
    },
    /**
     * メッセージ種別を取得する。
     */
    getMessageType(state) {
      return state._type;
    },
    /**
     * メッセージパラメータ１を取得する。
     */
    getMessageParm1(state) {
      return state._messageParm1;
    },
    /**
     * メッセージパラメータ２を取得する。
     */
    getMessageParm2(state) {
      return state._messageParm2;
    },
    /**
     * メッセージパラメータ３を取得する。
     */
    getMessageParm3(state) {
      return state._messageParm3;
    },
  },
});

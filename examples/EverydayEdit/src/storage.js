import AsyncStorage from '@react-native-async-storage/async-storage';
const KEY='jinie-state';
export async function loadState(){return JSON.parse(await AsyncStorage.getItem(KEY)||'null');}
export async function saveState(value){await AsyncStorage.setItem(KEY,JSON.stringify(value));}

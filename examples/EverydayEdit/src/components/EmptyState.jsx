import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function EmptyState({title='Nothing here yet',message='Try another search',onReset}) { return <View style={{padding:30,alignItems:'center',gap:12}}><Text style={{fontSize:36}}>◇</Text><Text style={{fontWeight:'700',fontSize:20}}>{title}</Text><Text style={{color:'#888'}}>{message}</Text>{onReset&&<Pressable accessibilityRole='button' onPress={onReset}><Text style={{color:'#7856d8'}}>Reset</Text></Pressable>}</View>; }

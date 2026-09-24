import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function HeroBanner({title='New discoveries',subtitle='Curated for everyday life',primary='#7856d8',onPress}) { return <View style={{padding:24,borderRadius:24,backgroundColor:primary}}><Text style={{fontSize:30,fontWeight:'800',color:'white'}}>{title}</Text><Text style={{color:'white',marginVertical:14}}>{subtitle}</Text><Pressable accessibilityRole='button' onPress={onPress}><Text style={{color:'white',fontWeight:'700'}}>Explore collection →</Text></Pressable></View>; }

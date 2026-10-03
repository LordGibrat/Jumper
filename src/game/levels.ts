import type {Shoe} from '../types';

type Stage={name:string;start:[number,number];pads:[number,number,number][];object:string;night?:boolean};
const START:[[number,number],[number,number],[number,number],[number,number],[number,number]]=[[50,400],[50,450],[50,200],[50,450],[20,250]];
const PADS:[[number,number,number][],[number,number,number][],[number,number,number][],[number,number,number][],[number,number,number][]]=[
  [[300,450,150]],[[400,300,120]],[[300,350,100],[600,500,100]],[[300,300,100],[550,150,100]],[[190,400,80],[440,250,80],[610,380,170]]
];
const stages=(names:string[],objects:string[],night=true):Stage[]=>names.map((name,i)=>({name,start:START[i],pads:PADS[i],object:objects[i],...(night&&i===4?{night:true}:{})}));
export const CITIES=[
 {name:'Home City',accent:'#55d6be',levels:stages(['Street','Courtyard','Bus stop','City centre','Night square'],['crates','mailbox','office','dumpster','chimney'])},
 {name:'New York',accent:'#ffb84d',levels:stages(['Brooklyn','Queens','Central Park','Times Square','Liberty Island'],['luggage','hotdog_cart','subway','luggage','hotdog_cart'])},
 {name:'Astana',accent:'#80aaff',levels:stages(['Steppe','Avenue','Khan Shatyr','Expo','Baiterek'],['yurt','mailbox','dome','yurt','dome'])},
 {name:'Tokyo',accent:'#ff6b9e',levels:stages(['Shibuya','Asakusa','Akihabara','Shinjuku','Tokyo Tower'],['sushi_cart','torii','vending_jp','sushi_cart','torii'])},
 {name:'Paris',accent:'#c69cff',levels:stages(['Montmartre','Latin Quarter','Louvre','Champs-Élysées','Mars Field'],['book_stall','cafe','mailbox','book_stall','cafe'])},
 {name:'London',accent:'#7ce0ff',levels:stages(['Camden','Soho','Westminster','Piccadilly','Big Ben'],['phone_booth','double_decker','phone_booth','double_decker','phone_booth'])}
] as const;
export const SHOES: Shoe[]=[{id:'basic',name:'Everyday',desc:'Reliable and balanced.',price:0,jump:1,speed:1,spin:14,coins:1,color:'#e8eefc'},{id:'spring',name:'Springers',desc:'Jump much higher.',price:120,jump:1.3,speed:1,spin:14,coins:1,color:'#69e38b'},{id:'sprint',name:'Sprinters',desc:'Fly and spin faster.',price:120,jump:1,speed:1.35,spin:18,coins:1,color:'#5da7ff'},{id:'gold',name:'Gold Soles',desc:'All-rounder +50% coins.',price:400,jump:1.15,speed:1.15,spin:16,coins:1.5,color:'#ffd35d'}];

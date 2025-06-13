import { Extension } from '@tiptap/core'
import { Decoration, DecorationSet } from 'prosemirror-view'
import { Plugin } from 'prosemirror-state'

export const DropIndicator = Extension.create({
  name: 'dropIndicator',

  addProseMirrorPlugins() {
    return [
      new Plugin({
        state: {
          init() { return { pos: null } },
          apply(tr, value) {
            if (tr.getMeta('dropIndicator') !== undefined) {
              return { pos: tr.getMeta('dropIndicator') }
            }
            return { pos: null }
          }
        },
        props: {
          decorations(state) {
            const { pos } = this.getState(state)
            if (pos === null) return null
            return DecorationSet.create(state.doc, [
              Decoration.widget(pos, () => {
                const el = document.createElement('div')
                el.className = 'drop-indicator'
                return el
              }, { side: 1 })
            ])
          }
        }
      })
    ]
  }
}) 